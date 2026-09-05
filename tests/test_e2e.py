"""E2E — full user workflow: register -> ingest -> pipeline -> dashboard -> lineage"""

import io
import sys
import time
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from unittest.mock import patch

import pandas as pd
from fastapi.testclient import TestClient

with patch("src.core.database.init_db"):
    from api import app

client = TestClient(app)


def register_and_login(username: str, password: str):
    # Try register, ignore if exists
    client.post("/auth/register", json={"username": username, "password": password})
    resp = client.post("/auth/login", json={"username": username, "password": password})
    assert resp.status_code == 200, f"login failed: {resp.text}"
    data = resp.json()
    token = data["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    return {"username": username, "token": token, "headers": headers}


def generate_sample_df():
    import numpy as np

    df = pd.DataFrame(
        {
            "id": list(range(1, 21)),
            "score": [
                5.5,
                6.0,
                None,
                7.2,
                4.3,
                8.1,
                None,
                5.0,
                6.5,
                7.0,
                3.2,
                9.0,
                None,
                5.5,
                6.6,
                7.7,
                4.4,
                8.8,
                2.1,
                6.0,
            ],
            "group": [
                "A",
                "A",
                "B",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "A",
                "B",
                "B",
                "A",
                "B",
                "A",
                "B",
                "A",
                "B",
            ],
            "value": [10, 20, 30, 40, 50, 60, 70, 80, 90, 100, 110, 120, 130, 140, 150, 160, 170, 180, 190, 200],
        }
    )
    return df


def upload_dataset(user, df: pd.DataFrame):
    # Create CSV in memory and upload via /datasets/ingest
    csv_buf = io.StringIO()
    df.to_csv(csv_buf, index=False)
    csv_bytes = csv_buf.getvalue().encode("utf-8")
    filename = f"e2e_{uuid.uuid4().hex[:6]}.csv"
    files = {"file": (filename, io.BytesIO(csv_bytes), "text/csv")}
    resp = client.post("/datasets/ingest", files=files, headers=user["headers"])
    assert resp.status_code == 200, f"ingest failed: {resp.text}"
    data = resp.json()
    dataset_id = data["dataset_id"]
    # Fetch duckdb_table from DB
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        assert ds is not None
        table = ds.duckdb_table
    return type("DS", (), {"id": dataset_id, "dataset_name": filename, "duckdb_table": table, "table": table})()


def generate_pipeline(user, dataset, description: str):
    # Build minimal spec that will succeed on dataset's table
    # For "fill missing by mean" we create fill_missing on score column
    from src.warehouse.connection import get_conn

    conn = get_conn()
    try:
        # Inspect columns
        cols = (
            conn.execute(
                f'SELECT * FROM "{dataset.duckdb_table.split(".")[0]}"."{dataset.duckdb_table.split(".")[1]}" LIMIT 1'
            )
            .fetchdf()
            .columns.tolist()
        )
    finally:
        conn.close()
    # Choose a column with missing if exists, else first numeric
    target_col = "score" if "score" in cols else cols[0] if cols else "value"
    spec = {
        "name": f"e2e-pipe-{uuid.uuid4().hex[:4]}",
        "source": dataset.duckdb_table,
        "target": f"mart.e2e_{uuid.uuid4().hex[:6]}",
        "steps": [
            {"id": "s1", "op": "fill_missing", "params": {"column": target_col, "method": "mean"}, "depends_on": []},
            {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": ["s1"]},
        ],
    }
    # Create pipeline via API
    resp = client.post("/pipelines", json=spec, headers=user["headers"])
    assert resp.status_code == 200, f"create pipeline failed: {resp.text}"
    pid = resp.json()["pipeline_id"]
    spec["pipeline_id"] = pid
    return type(
        "Spec",
        (),
        {"pipeline_id": pid, "spec": spec, "source": spec["source"], "target": spec["target"], "steps": spec["steps"]},
    )()


def execute_pipeline(user, spec):
    # Run pipeline and poll until done
    resp = client.post(f"/pipelines/run?pipeline_id={spec.pipeline_id}", headers=user["headers"])
    assert resp.status_code == 200, f"run failed: {resp.text}"
    run_id = resp.json()["run_id"]
    # Poll up to 10s
    result = None
    for _ in range(15):
        time.sleep(0.6)
        r = client.get(f"/runs/{run_id}", headers=user["headers"])
        assert r.status_code == 200, f"get run failed: {r.text}"
        info = r.json()
        status = info.get("status")
        if status in ("done", "failed"):
            result = info
            break
    assert result is not None, "run did not complete in time"
    assert result["status"] == "done", f"run failed: {result}"
    # Return object with status and target
    return type(
        "Run",
        (),
        {"status": result["status"], "run_id": run_id, "target": spec.target, "result": result.get("result", {})},
    )()


def generate_dashboard(user, target):
    # target may be mart table string or dataset id; handle both
    # For E2E we generate from original dataset id (need dataset)
    # If target is string mart.*, we need to find dataset id that maps to source
    # Simplify: try to generate dashboard for the dataset that was ingested (find latest dataset)
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.username == user["username"]).order_by(Dataset.id.desc()).first()
        dataset_id = ds.id if ds else 1
    resp = client.post(f"/dashboards/generate?dataset_id={dataset_id}", headers=user["headers"])
    assert resp.status_code == 200, f"dashboard generate failed: {resp.text}"
    spec = resp.json().get("spec", resp.json())
    charts = spec.get("charts", []) if isinstance(spec, dict) else []
    # Also create a dashboard to persist
    try:
        client.post(
            "/dashboards", json={"name": f"e2e-dash-{uuid.uuid4().hex[:4]}", "spec": spec}, headers=user["headers"]
        )
    except Exception:
        pass
    return type("Dashboard", (), {"charts": charts, "spec": spec})()


def get_lineage(user, dataset_id):
    # Prefer API
    resp = client.get(f"/lineage/{dataset_id}", headers=user["headers"])
    if resp.status_code == 200:
        data = resp.json()
        return type(
            "Lineage",
            (),
            {
                "pipelines_count": data.get("pipelines_count", data.get("pipelines", 0)),
                "pipelines": data.get("pipelines", 0),
                "data": data,
            },
        )()
    else:
        from src.warehouse.lineage import get_lineage as _gl

        data = _gl(dataset_id)
        return type(
            "Lineage",
            (),
            {"pipelines_count": data.get("pipelines_count", 0), "pipelines": data.get("pipelines", 0), "data": data},
        )()


def test_full_workflow():
    # 1. Register + login (unique user)
    username = f"e2e_user_{uuid.uuid4().hex[:6]}"
    user = register_and_login(username, "pass123")

    # 2. Upload dataset
    df = generate_sample_df()
    dataset = upload_dataset(user, df)
    assert dataset.id is not None

    # 3. Generate pipeline
    spec = generate_pipeline(user, dataset, "fill missing by mean")
    assert spec.pipeline_id is not None

    # 4. Run pipeline
    run = execute_pipeline(user, spec)
    assert run.status == "done"

    # Verify mart table exists and has rows
    from src.warehouse.connection import get_conn

    conn = get_conn()
    try:
        schema, table = run.target.split(".")
        cnt = conn.execute(f'SELECT COUNT(*) FROM "{schema}"."{table}"').fetchone()[0]
        assert cnt >= 10
    finally:
        conn.close()

    # 5. Generate dashboard
    dashboard = generate_dashboard(user, run.target)
    assert len(dashboard.charts) >= 4, f"charts {dashboard.charts}"

    # 6. Verify lineage
    lineage = get_lineage(user, dataset.id)
    assert lineage.pipelines_count >= 1, f"lineage {lineage.data}"

    # Cleanup: delete user
    client.delete("/auth/user", headers=user["headers"])
