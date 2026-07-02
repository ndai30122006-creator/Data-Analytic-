"""Landing page tab"""
import streamlit as st


def render_landing_page() -> None:
    """Render the landing page when no dataset is loaded."""
    st.markdown("""
    <div class="hero-bg" style="text-align: center; padding: 3rem 2rem; margin: 2rem 0;">
        <h1 style="font-size: 2.5rem;">📊 Data Analyst Pro</h1>
        <p style="font-size: 1.2rem; color: #94a3b8; margin: 1rem 0;">
            Practical Statistics for Data Scientists, 2nd Edition
        </p>
        <p style="color: #cbd5e1; max-width: 600px; margin: 0 auto;">
            Upload a CSV or Excel file to begin exploring your data with statistical methods,
            interactive visualizations, and machine learning models.
        </p>
    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        <div class="hero-bg" style="padding: 1.5rem; text-align: center;">
            <h3>📈 Statistics</h3>
            <p style="color: #94a3b8;">Hypothesis tests, regression, A/B testing, bootstrap</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="hero-bg" style="padding: 1.5rem; text-align: center;">
            <h3>🔬 Analytics</h3>
            <p style="color: #94a3b8;">AutoML, anomaly detection, profiling, cleaning</p>
        </div>
        """, unsafe_allow_html=True)
    with col3:
        st.markdown("""
        <div class="hero-bg" style="padding: 1.5rem; text-align: center;">
            <h3>🤖 AI Insights</h3>
            <p style="color: #94a3b8;">Automated insights and recommendations</p>
        </div>
        """, unsafe_allow_html=True)