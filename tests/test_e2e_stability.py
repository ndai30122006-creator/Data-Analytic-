"""E2E ổn định (mục 7-12): ownership, validation, SQLi, upload, error shape, run logs, concurrency guard."""

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


def _user(suffix: str):
    username = f"stab_{suffix}_{uuid.uuid4().hex[:6]}"
    client.post("/auth/register", json={"username": username, "password": "pass123"})
    resp = client.post("/auth/login", json={"username": username, "password": "pass123"})
    assert resp.status_code == 200, resp.text
    return {"username": username, "headers": {"Authorization": f"Bearer {resp.json()['access_token']}"}}


def _upload(user, name: str = None, content: bytes = None, filename: str = None):
    if content is None:
        df = pd.DataFrame({"id": [1, 2, 3], "score": [5.0, 6.0, 7.0], "grp": ["A", "B", "A"]})
        buf = io.StringIO()
        df.to_csv(buf, index=False)
        content = buf.getvalue().encode()
    filename = filename or f"stab_{uuid.uuid4().hex[:6]}.csv"
    files = {"file": (filename, io.BytesIO(content), "text/csv")}
    resp = client.post("/datasets/ingest", files=files, headers=user["headers"])
    return resp


def _table_of(dataset_id: int):
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        return ds.duckdb_table


def test_error_shape_standardized():
    """Mục 11: lỗi 404 có {code, message, detail, trace_id}."""
    u = _user("err")
    r = client.get("/datasets/999999/profile", headers=u["headers"])
    assert r.status_code == 404
    body = r.json()
    assert set(("code", "message", "detail", "trace_id")) <= set(body.keys())
    assert body["code"] == "E404"


def test_api_key_validation():
    """Mục 2/11: key quá ngắn → 400 chuẩn."""
    u = _user("key")
    r = client.post("/auth/api-key", json={"api_key": "short"}, headers=u["headers"])
    assert r.status_code == 400
    assert r.json()["code"] == "E400"


def test_upload_empty_and_bad_ext():
    """Mục 5: file rỗng / sai định dạng → 400, không crash."""
    u = _user("upl")
    r = _upload(u, content=b"", filename="empty.csv")
    assert r.status_code == 400, r.text
    r = _upload(u, content=b"hello", filename="evil.txt")
    assert r.status_code == 400, r.text


def test_pipeline_spec_validation():
    """Mục 3: spec DAG sai / identifier sai → 400, không persist."""
    u = _user("spec")
    r = _upload(u)
    assert r.status_code == 200, r.text
    table = _table_of(r.json()["dataset_id"])
    bad_specs = [
        # depends_on không tồn tại
        {
            "name": "x",
            "source": table,
            "target": "mart.stab_x1",
            "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": ["nope"]}],
        },
        # cycle
        {
            "name": "x",
            "source": table,
            "target": "mart.stab_x2",
            "steps": [
                {"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": ["s2"]},
                {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": ["s1"]},
            ],
        },
        # identifier sai (SQLi qua tên bảng)
        {"name": "x", "source": 'raw.t"; DROP TABLE users; --', "target": "mart.stab_x3", "steps": []},
        # op không tồn tại
        {
            "name": "x",
            "source": table,
            "target": "mart.stab_x4",
            "steps": [{"id": "s1", "op": "no_such_op", "params": {}, "depends_on": []}],
        },
    ]
    for spec in bad_specs:
        r = client.post("/pipelines", json=spec, headers=u["headers"])
        assert r.status_code in (400, 403), f"{spec} -> {r.status_code} {r.text}"


def test_cross_user_source_forbidden():
    """Mục 6: user B không được preview/create pipeline trên bảng của user A."""
    a = _user("ownA")
    b = _user("ownB")
    r = _upload(a)
    assert r.status_code == 200, r.text
    table_a = _table_of(r.json()["dataset_id"])
    spec = {"name": "cross", "source": table_a, "target": "mart.stab_cross", "steps": []}
    r = client.post("/pipelines/preview", json=spec, headers=b["headers"])
    assert r.status_code == 403, r.text
    r = client.post("/pipelines", json=spec, headers=b["headers"])
    assert r.status_code == 403, r.text


def test_sql_injection_blocked():
    """Mục 4: sql op chứa DROP → run failed an toàn, không thực thi."""
    u = _user("sqli")
    r = _upload(u)
    assert r.status_code == 200, r.text
    table = _table_of(r.json()["dataset_id"])
    spec = {
        "name": "sqli",
        "source": table,
        "target": f"mart.stab_{uuid.uuid4().hex[:6]}",
        "steps": [{"id": "s1", "op": "sql", "params": {"query": "DROP TABLE users"}, "depends_on": []}],
    }
    r = client.post("/pipelines", json=spec, headers=u["headers"])
    assert r.status_code == 200, r.text
    pid = r.json()["pipeline_id"]
    r = client.post(f"/pipelines/run?pipeline_id={pid}", headers=u["headers"])
    assert r.status_code == 200, r.text
    run_id = r.json()["run_id"]
    import time

    for _ in range(15):
        time.sleep(0.6)
        info = client.get(f"/runs/{run_id}", headers=u["headers"]).json()
        if info.get("status") in ("done", "failed"):
            break
    assert info["status"] == "failed", info
    # users table vẫn còn (đăng nhập được)
    r = client.post("/auth/login", json={"username": u["username"], "password": "pass123"})
    assert r.status_code == 200


def test_run_logs_and_steps():
    """Mục 12: GET /runs/{id} có steps log từng bước."""
    u = _user("logs")
    r = _upload(u)
    assert r.status_code == 200, r.text
    table = _table_of(r.json()["dataset_id"])
    spec = {
        "name": "logtest",
        "source": table,
        "target": f"mart.stab_{uuid.uuid4().hex[:6]}",
        "steps": [{"id": "s1", "op": "drop_duplicates", "params": {}, "depends_on": []}],
    }
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    run_id = client.post(f"/pipelines/run?pipeline_id={pid}", headers=u["headers"]).json()["run_id"]
    import time

    for _ in range(15):
        time.sleep(0.6)
        info = client.get(f"/runs/{run_id}", headers=u["headers"]).json()
        if info.get("status") in ("done", "failed"):
            break
    assert info["status"] == "done", info
    assert "steps" in info and len(info["steps"]) >= 1
    assert info["steps"][0]["step_id"] == "s1"


def test_concurrent_same_pipeline_conflict():
    """Mục 10: giữ lock pipeline → run thứ 2 bị 409."""
    from src.api.routers.pipelines import _lock_for

    u = _user("conc")
    r = _upload(u)
    assert r.status_code == 200, r.text
    table = _table_of(r.json()["dataset_id"])
    spec = {"name": "conc", "source": table, "target": f"mart.stab_{uuid.uuid4().hex[:6]}", "steps": []}
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    lock = _lock_for(pid)
    assert lock is _lock_for(pid)
    lock.acquire()
    try:
        r = client.post(f"/pipelines/run?pipeline_id={pid}", headers=u["headers"])
        assert r.status_code == 409, r.text
        assert r.json()["code"] == "E409"
    finally:
        lock.release()


def test_versioning_pipeline_dashboard_dataset():
    """Muc 15: version=1 khi tao, tang khi PUT."""
    u = _user("ver")
    r = _upload(u)
    assert r.status_code == 200, r.text
    assert r.json().get("version") == 1
    dsid = r.json()["dataset_id"]
    table = _table_of(dsid)
    assert client.get(f"/datasets/{dsid}/profile", headers=u["headers"]).json().get("version") == 1
    spec = {"name": "vpipe", "source": table, "target": f"mart.stab_{uuid.uuid4().hex[:6]}", "steps": []}
    pid = client.post("/pipelines", json=spec, headers=u["headers"]).json()["pipeline_id"]
    assert client.get(f"/pipelines/{pid}", headers=u["headers"]).json().get("version") == 1
    r = client.put(f"/pipelines/{pid}", json={**spec, "name": "vpipe2"}, headers=u["headers"])
    assert r.status_code == 200 and r.json()["version"] == 2, r.text
    did = client.post(
        "/dashboards",
        json={"name": "vd", "spec": {"id": "d", "title": "t", "source": table, "charts": []}},
        headers=u["headers"],
    ).json()["dashboard_id"]
    assert client.get(f"/dashboards/{did}", headers=u["headers"]).json().get("version") == 1
    dash = client.get(f"/dashboards/{did}", headers=u["headers"]).json()
    r = client.put(f"/dashboards/{did}", json={"name": "vd2", "spec": dash["spec"]}, headers=u["headers"])
    assert r.status_code == 200 and r.json()["version"] == 2, r.text


def test_lineage_graph_shape():
    """Muc 13: /lineage tra nodes/edges truc quan."""
    u = _user("ling")
    r = _upload(u)
    assert r.status_code == 200, r.text
    dsid = r.json()["dataset_id"]
    r = client.get(f"/lineage/{dsid}", headers=u["headers"])
    assert r.status_code == 200, r.text
    body = r.json()
    assert isinstance(body.get("nodes"), list) and len(body["nodes"]) >= 1
    assert isinstance(body.get("edges"), list)
    assert body["nodes"][0]["kind"] == "dataset"
    # Tao brief + pipeline -> nodes tang
    client.post(f"/brief/{dsid}", headers=u["headers"])
    table = _table_of(dsid)
    client.post(
        "/pipelines",
        json={"name": "lp", "source": table, "target": f"mart.stab_{uuid.uuid4().hex[:6]}", "steps": []},
        headers=u["headers"],
    )
    body = client.get(f"/lineage/{dsid}", headers=u["headers"]).json()
    kinds = {n["kind"] for n in body["nodes"]}
    assert {"dataset", "brief", "pipeline"} <= kinds, kinds


def test_table_rows_paging_sort_search():
    """Muc Data Table Pro: paging/sort/search + ownership."""
    u = _user("rows")
    df = pd.DataFrame({"id": [3, 1, 2], "score": [9.0, 5.0, 7.0], "grp": ["B", "A", "A"]})
    buf = io.StringIO()
    df.to_csv(buf, index=False)
    files = {"file": (f"rows_{uuid.uuid4().hex[:6]}.csv", io.BytesIO(buf.getvalue().encode()), "text/csv")}
    dsid = client.post("/datasets/ingest", files=files, headers=u["headers"]).json()["dataset_id"]
    base = f"/datasets/{dsid}/rows"
    r = client.get(f"{base}?limit=2&offset=0", headers=u["headers"]).json()
    assert r["total"] == 3 and len(r["rows"]) == 2 and set(r["columns"]) == {"id", "score", "grp"}
    r = client.get(f"{base}?limit=2&offset=2", headers=u["headers"]).json()
    assert len(r["rows"]) == 1
    r = client.get(f"{base}?order_by=score&order_dir=desc", headers=u["headers"]).json()
    assert [x[1] for x in r["rows"]] == [9.0, 7.0, 5.0]
    bad = client.get(f"{base}?order_by=nope", headers=u["headers"])
    assert bad.status_code == 400
    r = client.get(f"{base}?q=B", headers=u["headers"]).json()
    assert r["total"] == 1
    # cross-user
    v = _user("rowsV")
    assert client.get(base, headers=v["headers"]).status_code == 404
    # table path + sql-ish order_by rejected
    table = _table_of(dsid)
    r = client.get(f"/tables/rows?table={table}&limit=5", headers=u["headers"]).json()
    assert r["total"] == 3
    assert client.get(f"/tables/rows?table={table}", headers=v["headers"]).status_code == 403
    assert client.get(f"/tables/rows?table={table}&order_by=id;DROP", headers=u["headers"]).status_code in (400, 403)


def test_dashboard_cross_user_forbidden():
    """Mục 6: user B không đọc dashboard của user A."""
    a = _user("dashA")
    b = _user("dashB")
    r = _upload(a)
    assert r.status_code == 200, r.text
    table = _table_of(r.json()["dataset_id"])
    spec = {"id": "d1", "title": "t", "source": table, "charts": []}
    did = client.post("/dashboards", json={"name": "priv", "spec": spec}, headers=a["headers"]).json()["dashboard_id"]
    r = client.get(f"/dashboards/{did}", headers=b["headers"])
    assert r.status_code == 404
    r = client.post(f"/dashboards/{did}/data", headers=b["headers"])
    assert r.status_code == 404
