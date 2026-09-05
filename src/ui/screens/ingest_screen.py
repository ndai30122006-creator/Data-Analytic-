"""Ingest screen — upload → preview 20 rows → confirm ingest (P1 Step 7)."""

import streamlit as st


def render_ingest_screen(*args, **kwargs):
    st.markdown("## 📥 Ingest — Upload & Profile")
    st.caption("Upload CSV/Excel → preview 20 rows → confirm ingest → raw.<name> DuckDB + profile_json (P1)")

    uploaded = st.file_uploader(
        "Upload CSV/Excel", type=["csv", "xlsx", "xls"], key="ingest_uploader", accept_multiple_files=False
    )

    if uploaded is not None:
        # Preview via helpers (reuse)
        from src.utils.helpers import load_and_process_data

        df = load_and_process_data(uploaded)
        if df is not None and not df.empty:
            st.markdown(f"**Preview 20 rows:** {len(df):,} rows × {len(df.columns)} cols")
            st.dataframe(df.head(20), use_container_width=True)

            # Profile preview via insights
            from src.core.insights import generate_data_summary

            with st.expander("Xem profile sẽ lưu (KHÔNG gửi raw cho LLM)", expanded=False):
                st.text(generate_data_summary(df))

            if st.button("Confirm Ingest → DuckDB raw", key="ingest_confirm", type="primary"):
                # P0 fix: frontend → API (not direct DB) when backend available
                token = st.session_state.get("access_token")
                if token:
                    try:
                        import requests

                        files = {"file": (uploaded.name, uploaded.getvalue(), "multipart/form-data")}
                        r = requests.post(
                            "http://localhost:8000/datasets/ingest",
                            files=files,
                            headers={"Authorization": f"Bearer {token}"},
                            timeout=30,
                        )
                        if r.ok:
                            st.success(f"Ingested via API: {r.json()}")
                            st.json(r.json())
                        else:
                            st.warning(f"API ingest failed {r.status_code}: {r.text[:200]} — fallback direct")
                            raise RuntimeError(r.text)
                    except Exception as api_e:
                        st.caption(f"Fallback direct (API {api_e})")
                        # Fallback direct (dev without backend)
                        try:
                            import json

                            from src.warehouse.ingest import ingest_file

                            user = st.session_state.get("username", "demo")
                            result = ingest_file(user, uploaded)
                            st.success(f"Ingested (fallback) {result['table']} ({result['rows']} rows)")
                            st.json({"table": result["table"], "quality": result.get("quality")})
                        except Exception as e:
                            st.error(f"Ingest failed: {e}")
                else:
                    # No token — direct (dev)
                    try:
                        import json

                        from src.warehouse.ingest import ingest_file

                        user = st.session_state.get("username", "demo")
                        result = ingest_file(user, uploaded)
                        st.success(f"Ingested (dev direct) {result['table']} ({result['rows']} rows)")
                        st.json({"table": result["table"], "quality": result.get("quality")})
                    except Exception as e:
                        st.error(f"Ingest failed: {e} — hãy đăng nhập để dùng API")
        else:
            st.error("Không đọc được file hoặc file rỗng")
    else:
        # Show registry
        from src.core.database import Dataset, SessionLocal

        with SessionLocal() as s:
            datasets = s.query(Dataset).all()
        if datasets:
            st.markdown(f"**Registry ({len(datasets)} datasets):**")
            for d in datasets[:10]:
                st.markdown(f"- `{d.dataset_name}` (id={d.id}) → `{d.duckdb_table}` — {d.rows} rows")
                if d.profile_json:
                    with st.expander(f"Profile {d.dataset_name}", expanded=False):
                        st.text(d.profile_json[:500])
        else:
            st.markdown('<div class="skeleton skeleton-card" style="height:100px"></div>', unsafe_allow_html=True)
            st.caption("Chưa có dataset nào trong registry")
