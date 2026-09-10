"""Plan 4 — strong integration tests: DAG + engine selection qua HTTP."""

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


def _user():
    username = f"ipe2e_{uuid.uuid4().hex[:6]}"
    client.post("/auth/register", json={"username": username, "password": "pass123"})
    resp = client.post("/auth/login", json={"username": username, "password": "pass123"})
    assert resp.status_code == 200, resp.text
    return {"username": username, "headers": {"Authorization": f"Bearer {resp.json()['access_token']}"}}


def _upload(user, n=200):
    import numpy as np

    rng = np.random.default_rng(11)
    df = pd.DataFrame(
        {
            "id": range(n),
            "grp": rng.choice(["A", "B"], n),
            "score": rng.normal(6.5, 1.5, n).round(2),
        }
    )
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    files = {"file": (f"e_{uuid.uuid4().hex[:6]}.csv", io.BytesIO(buf.getvalue().encode()), "text/csv")}
    r = client.post("/datasets/ingest", files=files, headers=user["headers"])
    assert r.status_code == 200, r.text
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        return s.query(Dataset).filter(Dataset.id == r.json()["dataset_id"]).first().duckdb_table


def _run_to_done(user, pid, timeout_s=30):
    run_id = client.post(f"/pipelines/run?pipeline_id={pid}", headers=user["headers"]).json()["run_id"]
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        time.sleep(1)
        info = client.get(f"/runs/{run_id}", headers=user["headers"]).json()
        if info.get("status") in ("done", "failed"):
            return info
    raise AssertionError("run timeout")


def test_http_diamond_merge_pandas():
    """Diamond DAG qua HTTP day du: create -> preview -> run -> steps + timings + hash."""
    u = _user()
    table = _upload(u)
    target = f"mart.ipe_{uuid.uuid4().hex[:6]}"
    spec = {
        "name": "diamond",
        "source": table,
        "target": target,
        "engine": "pandas",
        "steps": [
            {"id": "clean", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "agg", "op": "aggregate", "params": {"by": "grp", "agg": "mean"}, "depends_on": ["clean"]},
            {"id": "flt", "op": "filter", "params": {"query": "score >= 6"}, "depends_on": ["clean"]},
            {"id": "final", "op": "merge", "params": {"how": "concat"}, "depends_on": ["agg", "flt"]},
        ],
    }
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    prev = client.post("/pipelines/preview", json=spec, headers=u["headers"]).json()
    assert prev["status"] == "done", prev
    assert prev["engine_used"] == "pandas" and prev["spec_hash"]
    info = _run_to_done(u, pid)
    assert info["status"] == "done", info
    assert info["engine"] == "pandas" and info["spec_hash"]
    assert info["duration_s"] is not None and info["rows_out"] == info["result"]["rows"]
    assert {s["step_id"] for s in info["steps"]} == {"clean", "agg", "flt", "final"}
    assert set(info["result"]["step_timings"]) == {"clean", "agg", "flt", "final"}


def test_http_engine_duckdb_selection():
    """Chon engine duckdb qua HTTP: run + engine_used + reproduce."""
    u = _user()
    table = _upload(u)
    target = f"mart.ipe_{uuid.uuid4().hex[:6]}"
    spec = {
        "name": "dq",
        "source": table,
        "target": target,
        "engine": "duckdb",
        "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []}],
    }
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    info = _run_to_done(u, pid)
    assert info["status"] == "done", info
    assert info["engine"] == "duckdb"
    rep = client.get(f"/pipelines/{pid}/reproduce", headers=u["headers"]).json()
    assert rep["spec_hash"] == info["spec_hash"] and rep["engine"] == "duckdb"
    st = client.get(f"/pipelines/{pid}/stats", headers=u["headers"]).json()
    assert st["runs"] >= 1 and st["success_rate"] == 1.0
    assert st["engines"].get("duckdb", 0) >= 1 and st["last_duration_s"] is not None


def test_http_contract_gate_blocks():
    """Contract fail -> preview + run deu blocked, co gate report."""
    u = _user()
    table = _upload(u)
    spec = {
        "name": "gated",
        "source": table,
        "target": f"mart.ipe_{uuid.uuid4().hex[:6]}",
        "engine": "pandas",
        "contract": {"min_rows": 1_000_000, "columns": {"nope_col": {"dtype": "float"}}},
        "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []}],
    }
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    prev = client.post("/pipelines/preview", json=spec, headers=u["headers"]).json()
    assert prev["status"] == "failed" and prev["gate"]["passed"] is False, prev
    assert any("nope_col" in v or "min_rows" in v for v in prev["gate"]["violations"]), prev
    info = _run_to_done(u, pid)
    assert info["status"] == "failed"
    assert info["result"]["gate"]["passed"] is False


def test_http_contract_pass_and_stats_steps():
    u = _user()
    table = _upload(u)
    spec = {
        "name": "ok",
        "source": table,
        "target": f"mart.ipe_{uuid.uuid4().hex[:6]}",
        "contract": {
            "min_rows": 10,
            "max_missing_pct": 50,
            "columns": {"score": {"dtype": "float", "min": 0, "max": 15}},
        },
        "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []}],
    }
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    info = _run_to_done(u, pid)
    assert info["status"] == "done", info
    assert info["result"]["gate"]["passed"] is True
    st = client.get(f"/pipelines/{pid}/stats", headers=u["headers"]).json()
    assert st["step_status"].get("s1:done", 0) >= 1
