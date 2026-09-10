"""Tests cho dot review: target mart.*, dup step id, provider, analysis 400, UNIQUE, proposal hash."""

import io
import sys
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
    username = f"rev_{uuid.uuid4().hex[:6]}"
    client.post("/auth/register", json={"username": username, "password": "pass123"})
    resp = client.post("/auth/login", json={"username": username, "password": "pass123"})
    return {"username": username, "headers": {"Authorization": f"Bearer {resp.json()['access_token']}"}}


def _upload(user, suffix=""):
    df = pd.DataFrame({"id": [1, 2], "v": [1.0, 2.0]})
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    files = {"file": (f"r{suffix}_{uuid.uuid4().hex[:6]}.csv", io.BytesIO(buf.getvalue().encode()), "text/csv")}
    r = client.post("/datasets/ingest", files=files, headers=user["headers"])
    assert r.status_code == 200, r.text
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        return s.query(Dataset).filter(Dataset.id == r.json()["dataset_id"]).first().duckdb_table


def test_target_must_be_mart():
    u = _user()
    table = _upload(u)
    spec = {"name": "x", "source": table, "target": "raw.evil", "steps": []}
    r = client.post("/pipelines", json=spec, headers=u["headers"])
    assert r.status_code == 400 and "mart" in r.json()["detail"].lower()


def test_duplicate_step_id_clear_error():
    import pytest

    from src.pipeline.spec_schema import PipelineSpec

    spec = PipelineSpec(
        name="x",
        source="raw.t",
        target="mart.t",
        steps=[
            {"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []},
            {"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []},
        ],
    )
    with pytest.raises(ValueError, match="Duplicate step id"):
        spec.validate_dag()


def test_provider_saved_and_used():
    u = _user()
    r = client.post("/auth/api-key", json={"api_key": "sk-test-key-123", "provider": "gemini"}, headers=u["headers"])
    assert r.status_code == 200 and r.json()["provider"] == "gemini"
    from src.core.database import get_api_provider

    assert get_api_provider(u["username"]) == "gemini"
    r = client.post("/auth/api-key", json={"api_key": "sk-test-key-123", "provider": "nope"}, headers=u["headers"])
    assert r.status_code == 400


def test_analysis_ab_missing_keys_400():
    u = _user()
    r = client.post(
        "/analysis/run",
        json={"dataset_name": "inline", "analysis_type": "ab_test", "params": {}},
        headers=u["headers"],
    )
    assert r.status_code == 400


def test_create_dataset_negative_422_and_duplicate_400():
    u = _user()
    r = client.post("/datasets", json={"dataset_name": "n", "rows": -1}, headers=u["headers"])
    assert r.status_code == 422
    r = client.post("/datasets", json={"dataset_name": "dup"}, headers=u["headers"])
    assert r.status_code == 200
    r = client.post("/datasets", json={"dataset_name": "dup"}, headers=u["headers"])
    assert r.status_code == 400


def test_ingest_duplicate_filename_clean_400():
    u = _user()
    df = pd.DataFrame({"a": [1]})
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    content = buf.getvalue().encode()
    fn = f"same_{uuid.uuid4().hex[:6]}.csv"
    files = {"file": (fn, io.BytesIO(content), "text/csv")}
    assert client.post("/datasets/ingest", files=files, headers=u["headers"]).status_code == 200
    files = {"file": (fn, io.BytesIO(content), "text/csv")}
    r = client.post("/datasets/ingest", files=files, headers=u["headers"])
    assert r.status_code == 400 and "already exists" in r.json()["detail"]


def test_proposal_spec_hash_and_reproduce_match():
    u = _user()
    table = _upload(u)
    gen = client.post(
        "/pipelines/generate",
        json={"source": table, "target": f"mart.rev_{uuid.uuid4().hex[:6]}", "description": "xoa trung"},
        headers=u["headers"],
    ).json()
    assert gen["spec_hash"] and len(gen["spec_hash"]) == 64
    pid = client.post(f"/pipelines/proposals/{gen['proposal_id']}/approve", headers=u["headers"])
    assert pid.status_code == 200
    spec = client.get(f"/pipelines/proposals/{gen['proposal_id']}", headers=u["headers"]).json()["spec"]
    pl = client.post("/pipelines", json={**spec, "proposal_id": gen["proposal_id"]}, headers=u["headers"]).json()
    rep = client.get(f"/pipelines/{pl['pipeline_id']}/reproduce", headers=u["headers"]).json()
    assert rep["spec_hash"] == gen["spec_hash"]
    assert rep["proposal"]["proposal_id"] == gen["proposal_id"]
    assert rep["proposal"]["status"] == "approved"


def test_500_no_leak():
    r = client.get("/datasets/abc/profile", headers={"Authorization": "Bearer fake"})
    assert r.status_code in (401, 404, 422)
