"""Tests production-grade AI: proposals, 4-layer validation, cost, approval gate."""

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
    username = f"prop_{uuid.uuid4().hex[:6]}"
    client.post("/auth/register", json={"username": username, "password": "pass123"})
    resp = client.post("/auth/login", json={"username": username, "password": "pass123"})
    return {"username": username, "headers": {"Authorization": f"Bearer {resp.json()['access_token']}"}}


def _upload(user):
    df = pd.DataFrame({"id": [1, 2, 2, 3], "score": [5.0, 6.0, 6.0, 9.0], "grp": ["A", "B", "B", "A"]})
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    files = {"file": (f"p_{uuid.uuid4().hex[:6]}.csv", io.BytesIO(buf.getvalue().encode()), "text/csv")}
    r = client.post("/datasets/ingest", files=files, headers=user["headers"])
    assert r.status_code == 200, r.text
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        return s.query(Dataset).filter(Dataset.id == r.json()["dataset_id"]).first().duckdb_table


def test_proposal_flow_rule_based():
    """Generate (no key) -> proposal proposed + validations + cost + dry-run."""
    u = _user()
    table = _upload(u)
    target = f"mart.prop_{uuid.uuid4().hex[:6]}"
    r = client.post(
        "/pipelines/generate",
        json={"source": table, "target": target, "description": "xoa trung"},
        headers=u["headers"],
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["status"] == "proposed" and body["proposal_id"]
    assert body["model_used"] == "rule-based"
    v = body["validations"]
    assert v["schema_ok"] and v["safety_ok"] and v["dry_run_ok"], v
    assert body["cost"]["source_rows"] == 4
    assert body["cost"]["recommended_engine"] == "pandas"
    assert body["dry_run"]["status"] == "done"


def test_approval_gate_blocks_unapproved():
    """Create voi proposal chua approved -> 403; approve -> tao duoc."""
    u = _user()
    table = _upload(u)
    target = f"mart.prop_{uuid.uuid4().hex[:6]}"
    pid = client.post(
        "/pipelines/generate",
        json={"source": table, "target": target, "description": "xoa trung"},
        headers=u["headers"],
    ).json()["proposal_id"]
    spec = client.get(f"/pipelines/proposals/{pid}", headers=u["headers"]).json()["spec"]
    # Chua approve -> 403
    r = client.post("/pipelines", json={**spec, "proposal_id": pid}, headers=u["headers"])
    assert r.status_code == 403, r.text
    assert "approve" in r.json()["detail"].lower()
    # Approve -> tao duoc
    r = client.post(f"/pipelines/proposals/{pid}/approve", headers=u["headers"])
    assert r.status_code == 200 and r.json()["status"] == "approved"
    r = client.post("/pipelines", json={**spec, "proposal_id": pid}, headers=u["headers"])
    assert r.status_code == 200, r.text
    # Approve lai -> 400
    r = client.post(f"/pipelines/proposals/{pid}/approve", headers=u["headers"])
    assert r.status_code == 400


def test_proposal_cross_user_and_reject():
    u, v = _user(), _user()
    table = _upload(u)
    pid = client.post(
        "/pipelines/generate",
        json={"source": table, "target": f"mart.prop_{uuid.uuid4().hex[:6]}", "description": "x"},
        headers=u["headers"],
    ).json()["proposal_id"]
    assert client.get(f"/pipelines/proposals/{pid}", headers=v["headers"]).status_code == 404
    assert client.post(f"/pipelines/proposals/{pid}/reject", headers=v["headers"]).status_code == 404
    r = client.post(f"/pipelines/proposals/{pid}/reject", headers=u["headers"])
    assert r.json()["status"] == "rejected"
    # Rejected -> create bi chan
    spec = client.get(f"/pipelines/proposals/{pid}", headers=u["headers"]).json()["spec"]
    r = client.post("/pipelines", json={**spec, "proposal_id": pid}, headers=u["headers"])
    assert r.status_code == 403


def test_proposal_safety_layer():
    """Target ngoai mart.* hoac sql nguy hiem -> safety fail (van luu proposal)."""
    u = _user()
    table = _upload(u)
    # Truc tiep goi validator layers
    from src.api.routers.pipelines import _estimate_cost, _validate_proposal_layers

    bad = {"name": "x", "source": table, "target": "raw.evil", "steps": []}
    v = _validate_proposal_layers(bad, ["id"])
    assert not v["safety_ok"] and v["safety_errors"]
    assert v["schema_ok"]  # DAG rong van hop le schema
    cost = _estimate_cost(table, [])
    assert cost["source_rows"] == 4 and cost["recommended_engine"] == "pandas"
