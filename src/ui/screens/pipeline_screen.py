"""Pipeline screen — NL -> spec -> dry-run -> run -> history (Plan 04)."""

import json

import streamlit as st
import yaml


def render_pipeline_screen(*args, **kwargs):
    st.markdown("## ⚙️ Pipeline — AI ETL/ELT")
    st.caption("Mô tả tiếng Việt → AI sinh PipelineSpec YAML → dry-run 100 rows → run → history (Plan 04)")

    # Dataset selector from warehouse
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        datasets = s.query(Dataset).all()
    if not datasets:
        st.info("Chưa có dataset. Upload ở Ingest trước.")
        return

    opts = {f"{d.dataset_name} (id={d.id})": d for d in datasets}
    sel = st.selectbox("Chọn dataset", list(opts.keys()), key="pipe_ds")
    ds = opts[sel]
    source = f"raw.{ds.dataset_name.lower().replace(' ', '_')}"
    target = f"mart.{ds.dataset_name.lower().replace(' ', '_')}"

    # Show columns from profile or DB
    try:
        from src.warehouse.connection import get_conn

        conn = get_conn()
        cols = [r[1] for r in conn.execute(f"PRAGMA table_info('{source}')").fetchall()]
        conn.close()
    except Exception:
        cols = []

    st.markdown(f"**Source:** `{source}` → **Target:** `{target}` | Columns: {', '.join(cols[:8])}")

    nl = st.text_area(
        "Mô tả pipeline (tiếng Việt)",
        placeholder="VD: điền missing cột điểm bằng median, xóa dòng trùng theo ma_sv, tạo cột xep_loai",
        height=100,
        key="pipe_nl",
    )

    # Generate spec via AI or fallback template
    if "pipe_spec" not in st.session_state:
        st.session_state.pipe_spec = ""

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Generate Spec (AI)", key="pipe_gen"):
            api_key = st.session_state.get("ai_api_key", "")
            provider = st.session_state.get("ai_provider", "openai")
            if api_key:
                from src.core.ai_service import get_ai_service
                from src.prompts.etl_author import build_prompt

                svc = get_ai_service(api_key, provider)
                prompt = build_prompt(nl, cols, source, target)
                if svc._init_llm() and svc._llm is not None:
                    msgs = "\n".join([f"{m['role']}: {m['content']}" for m in prompt])
                    resp = svc._llm.invoke(msgs)
                    st.session_state.pipe_spec = resp.content[:4000]
                else:
                    st.session_state.pipe_spec = _fallback_spec(nl, source, target, cols)
            else:
                st.session_state.pipe_spec = _fallback_spec(nl, source, target, cols)
            st.success("Đã sinh spec (xem editor)")

    with col2:
        if st.button("Template Spec", key="pipe_tpl"):
            st.session_state.pipe_spec = _fallback_spec(nl, source, target, cols)

    spec_text = st.text_area(
        "Spec YAML (editable)", value=st.session_state.pipe_spec, height=220, key="pipe_spec_editor"
    )

    c1, c2 = st.columns(2)
    with c1:
        if st.button("Dry-run (100 rows)", key="pipe_dry"):
            res = _run_spec(spec_text, sample=True)
            st.json(res)
            if res.get("status") == "done":
                st.success(f"Dry-run OK: {res['rows']} rows preview")
                st.dataframe(res.get("preview", []))
            else:
                st.error(res.get("error"))

    with c2:
        if st.button("Run (write mart)", key="pipe_run", type="primary"):
            res = _run_spec(spec_text, sample=False)
            st.json(res)
            if res.get("status") == "done":
                st.success(f"Run done → {res['target']} ({res['rows']} rows)")
            else:
                st.error(res.get("error"))

    with st.expander("History (skeleton)", expanded=False):
        st.caption("Sẽ lưu pipeline_runs + steps ở DB (P3). Hiện chỉ preview dry-run/run.")


def _fallback_spec(nl: str, source: str, target: str, cols: list) -> str:
    # Simple template spec
    spec = {
        "name": "clean-pipeline",
        "source": source,
        "target": target,
        "steps": [
            {
                "id": "s1",
                "op": "fill_missing",
                "params": {"column": cols[0] if cols else "col", "method": "median"},
                "depends_on": [],
            },
            {"id": "s2", "op": "drop_duplicates", "params": {}, "depends_on": ["s1"]},
        ],
    }
    return yaml.safe_dump(spec, allow_unicode=True, sort_keys=False)


def _run_spec(spec_text: str, sample: bool = False):
    try:
        spec_dict = yaml.safe_load(spec_text) or json.loads(spec_text)
        from src.pipeline.spec_schema import PipelineSpec

        spec = PipelineSpec(**spec_dict)
        from src.pipeline.executor import execute

        return execute(spec, sample=sample)
    except Exception as e:
        return {"status": "failed", "error": str(e)}
