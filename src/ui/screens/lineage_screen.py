"""Lineage screen — dataset -> pipelines -> dashboards (P5)."""

import streamlit as st


def render_lineage_screen(*args, **kwargs):
    st.markdown("## 🔗 Lineage — Dataset → Pipeline → Dashboard")
    st.caption("Truy vết nguồn gốc (Plan P5) — đọc từ SQLite metadata")
    from src.core.database import Dataset, SessionLocal

    with SessionLocal() as s:
        datasets = s.query(Dataset).all()
    if not datasets:
        st.info("Chưa có dataset")
        return
    opts = {f"{d.dataset_name} (id={d.id})": d for d in datasets}
    sel = st.selectbox("Chọn dataset", list(opts.keys()), key="lin_ds")
    ds = opts[sel]
    from src.warehouse.lineage import get_lineage

    lin = get_lineage(ds.id)
    st.json(lin)
    st.markdown(
        f"**Table:** `{lin.get('table')}` | **Briefs:** {lin.get('briefs')} | **Dashboards:** {lin.get('dashboards')}"
    )
