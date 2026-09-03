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
                try:
                    from src.warehouse.ingest import ingest_file
                    from src.warehouse.registry import register_dataset
                    import json

                    # Use current user from session or demo
                    user = st.session_state.get("username", "demo")
                    result = ingest_file(user, uploaded)
                    # Register (if ingest_file already does, skip)
                    # For now, result already registered via API path, but direct warehouse path:
                    # Ensure registry
                    try:
                        ds = register_dataset(
                            user,
                            uploaded.name,
                            result["table"],
                            file_path=uploaded.name,
                            profile_json=(
                                json.dumps(result["profile"], ensure_ascii=False)
                                if isinstance(result["profile"], dict)
                                else result["profile"]
                            ),
                        )
                        st.success(
                            f"Ingested {uploaded.name} → {result['table']} ({result['rows']} rows). Profile lưu registry id={ds.id}"
                        )
                    except Exception as reg_e:
                        st.success(f"Ingested {result['table']} ({result['rows']} rows) — {reg_e}")
                    st.json({"table": result["table"], "quality": result.get("quality")})
                except Exception as e:
                    st.error(f"Ingest failed: {e}")
        else:
            st.error("Không đọc được file hoặc file rỗng")
    else:
        # Show registry
        from src.core.database import SessionLocal, Dataset

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
