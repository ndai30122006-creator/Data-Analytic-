"""Brief screen — 1-click brief from profile (Plan 03)."""

import json

import streamlit as st


def _get_profile_for_dataset(dataset_id: int) -> dict:
    """Fetch profile_json from DB (no raw data)."""
    from src.core.database import SessionLocal, Dataset
    import json as _json

    with SessionLocal() as s:
        ds = s.query(Dataset).filter(Dataset.id == dataset_id).first()
        if ds and ds.profile_json:
            try:
                return _json.loads(ds.profile_json)
            except Exception:
                return {"raw_profile": ds.profile_json, "table": ds.duckdb_table, "rows": ds.rows, "cols": ds.cols}
        if ds:
            return {"table": ds.duckdb_table, "rows": ds.rows, "cols": ds.cols, "name": ds.dataset_name}
    return {}


def render_brief_screen(*args, **kwargs):
    st.markdown("## 📋 Brief — AI Data Summary")
    st.caption("Profile JSON → narrative (LLM chỉ nhận profile, fallback rule-based) — Plan 03")

    # List datasets from registry
    from src.core.database import SessionLocal, Dataset, Brief

    with SessionLocal() as s:
        datasets = s.query(Dataset).all()
    if not datasets:
        st.info("Chưa có dataset. Upload ở Ingest trước.")
        st.markdown('<div class="skeleton skeleton-card" style="height:100px"></div>', unsafe_allow_html=True)
        return

    opts = {f"{d.dataset_name} (id={d.id})": d for d in datasets}
    sel_label = st.selectbox("Chọn dataset", list(opts.keys()), key="brief_ds")
    ds = opts[sel_label]

    if st.button("Generate Brief", key="brief_gen", type="primary"):
        profile = _get_profile_for_dataset(ds.id)
        # Try AI gateway if BYOK key exists
        api_key = st.session_state.get("ai_api_key") or ""
        provider = st.session_state.get("ai_provider", "openai")
        content = ""
        model_used = "rule-based"
        try:
            if api_key:
                from src.core.ai_service import get_ai_service
                from src.prompts.briefer import build_prompt

                svc = get_ai_service(api_key, provider)
                # Build prompt from profile only
                prompt = build_prompt(profile)
                # Use ai_service internal LLM if available, else fallback
                # We reuse fallback via briefer directly for now
                from src.prompts.briefer import generate_brief_fallback

                # Try LLM invoke via ai_service if _llm available
                if svc._init_llm() and svc._llm is not None:
                    # Simple invoke
                    msgs = "\n".join([f"{m['role']}: {m['content']}" for m in prompt])
                    resp = svc._llm.invoke(msgs)
                    content = resp.content[:4000]
                    model_used = provider
                else:
                    content = generate_brief_fallback(profile)
            else:
                from src.prompts.briefer import generate_brief_fallback

                content = generate_brief_fallback(profile)
        except Exception as e:
            from src.prompts.briefer import generate_brief_fallback

            content = generate_brief_fallback(profile) + f"\n\n(LLM fallback do lỗi: {e})"

        # Save versioned brief
        with SessionLocal() as s:
            max_v = s.query(Brief).filter(Brief.dataset_id == ds.id).count()
            b = Brief(dataset_id=ds.id, version=max_v + 1, content=content, model_used=model_used)
            s.add(b)
            s.commit()
            st.success(f"Đã lưu Brief v{b.version} ({model_used})")

    # List brief versions
    with SessionLocal() as s:
        briefs = s.query(Brief).filter(Brief.dataset_id == ds.id).order_by(Brief.version.desc()).all()
    if briefs:
        st.markdown(f"**Lịch sử ({len(briefs)} versions):**")
        for b in briefs[:5]:
            with st.expander(f"v{b.version} — {b.model_used} — {b.created_at}", expanded=(b == briefs[0])):
                st.markdown(b.content)
                st.download_button(
                    f"Export v{b.version} Markdown",
                    b.content.encode("utf-8"),
                    f"brief_{ds.dataset_name}_v{b.version}.md",
                    "text/markdown",
                    key=f"brief_dl_{b.id}",
                )
    else:
        st.caption("Chưa có brief nào cho dataset này.")
