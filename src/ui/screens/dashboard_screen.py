"""Dashboard screen — AI spec -> renderer + edit + export (Plan 05)."""

import json

import streamlit as st


def render_dashboard_screen(*args, **kwargs):
    st.markdown("## 📊 Dashboard — AI Generation")
    st.caption("AI đề xuất 4-6 charts từ DashboardSpec, renderer Plotly, chỉnh tay, lưu/export (Plan 05)")

    # Dataset selector (mart)
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        datasets = s.query(Dataset).all()
    if not datasets:
        st.info("Chưa có dataset. Ingest trước.")
        return

    opts = {f"{d.dataset_name} (id={d.id})": d for d in datasets}
    sel = st.selectbox("Chọn dataset (mart)", list(opts.keys()), key="dash_ds")
    ds = opts[sel]
    source = ds.duckdb_table or f"mart.{ds.dataset_name.lower().replace(' ', '_')}"

    # Fetch profile + brief for author
    profile = {}
    try:
        import json as _json

        if ds.profile_json:
            profile = _json.loads(ds.profile_json)
    except Exception:
        profile = {"table": source, "rows": ds.rows, "cols": ds.cols}

    brief_text = ""
    try:
        from src.core.database import Brief

        with SessionLocal() as s:
            b = s.query(Brief).filter(Brief.dataset_id == ds.id).order_by(Brief.version.desc()).first()
            if b:
                brief_text = b.content[:500]
    except Exception:
        pass

    if st.button("Generate Dashboard (AI)", key="dash_gen", type="primary"):
        api_key = st.session_state.get("ai_api_key", "")
        provider = st.session_state.get("ai_provider", "openai")
        if api_key:
            from src.core.ai_service import get_ai_service
            from src.prompts.dashboard_author import build_prompt

            svc = get_ai_service(api_key, provider)
            prompt = build_prompt(profile, brief_text, source)
            if svc._init_llm() and svc._llm is not None:
                msgs = "\n".join([f"{m['role']}: {m['content']}" for m in prompt])
                resp = svc._llm.invoke(msgs)
                try:
                    spec_dict = json.loads(resp.content)
                except Exception:
                    from src.prompts.dashboard_author import fallback_spec

                    spec_dict = fallback_spec(profile, source)
            else:
                from src.prompts.dashboard_author import fallback_spec

                spec_dict = fallback_spec(profile, source)
        else:
            from src.prompts.dashboard_author import fallback_spec

            spec_dict = fallback_spec(profile, source)
        st.session_state["dash_spec"] = spec_dict
        st.success("Đã sinh DashboardSpec (xem editor)")

    spec_dict = st.session_state.get("dash_spec")
    if not spec_dict:
        # Fallback preview
        from src.prompts.dashboard_author import fallback_spec

        spec_dict = fallback_spec(profile, source)
        st.caption("Preview fallback spec (chưa generate)")

    # Editable JSON
    spec_text = st.text_area(
        "Spec JSON (editable, chỉ 6 types: kpi/bar/hist/box/line/scatter)",
        value=json.dumps(spec_dict, ensure_ascii=False, indent=2),
        height=220,
        key="dash_spec_editor",
    )

    if st.button("Render Dashboard", key="dash_render"):
        try:
            spec_dict2 = json.loads(spec_text)
            from src.dashboard.renderer import render
            from src.dashboard.spec_schema import DashboardSpec

            spec = DashboardSpec(**spec_dict2)
            figs = render(spec)
            for fig in figs:
                st.plotly_chart(fig, use_container_width=True)
            # Save to DB
            import json as _json

            from src.core.database import Dashboard

            with SessionLocal() as s:
                d = Dashboard(name=spec.title, spec_json=_json.dumps(spec_dict2, ensure_ascii=False), owner="local")
                s.add(d)
                s.commit()
                st.success(f"Đã lưu Dashboard id={d.id} — {spec.title}")
            # Export
            st.download_button(
                "Export Spec JSON",
                json.dumps(spec_dict2, ensure_ascii=False, indent=2).encode("utf-8"),
                f"dashboard_{spec.id}.json",
                "application/json",
                key="dash_export",
            )
        except Exception as e:
            st.error(f"Render failed: {e}")

    with st.expander("Saved Dashboards", expanded=False):
        try:
            from src.core.database import Dashboard

            with SessionLocal() as s:
                dashes = s.query(Dashboard).order_by(Dashboard.id.desc()).limit(10).all()
            for d in dashes:
                st.markdown(f"**{d.name}** (id={d.id}) — {d.created_at}")
        except Exception:
            st.caption("Chưa có dashboard nào")
