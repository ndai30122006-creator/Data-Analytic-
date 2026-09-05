"""Settings screen — BYOK (P0 Commit 3)."""

import streamlit as st


def render_settings_screen(*args, **kwargs):
    st.markdown("## ⚙️ Settings — BYOK")
    st.caption("Bring Your Own Key — OpenAI / Gemini, lưu vào users.api_key_ai via POST /auth/api-key")

    provider = st.selectbox(
        "Provider",
        ["openai", "gemini"],
        key="settings_provider",
        index=0 if st.session_state.get("ai_provider", "openai") == "openai" else 1,
    )
    api_key = st.text_input(
        "API Key",
        value=st.session_state.get("ai_api_key", ""),
        type="password",
        key="settings_api_key",
        help="Lưu local, không gửi raw data cho LLM",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Save Key", key="settings_save"):
            st.session_state["ai_provider"] = provider
            st.session_state["ai_api_key"] = api_key
            st.success(
                f"Saved provider={provider} (session). Để persist server, gọi POST /auth/api-key sau khi đăng nhập."
            )
            # Try to persist via API if logged in (requires JWT)
            try:
                import requests

                token = st.session_state.get("access_token")
                if token:
                    r = requests.post(
                        "http://localhost:8000/auth/api-key",
                        json={"api_key": api_key},
                        headers={"Authorization": f"Bearer {token}"},
                        timeout=5,
                    )
                    if r.ok:
                        st.success("Đã lưu lên server (DB).")
                    else:
                        st.warning(f"Server lưu thất bại: {r.text[:200]}")
                else:
                    st.caption("Chưa đăng nhập — chỉ lưu session. Đăng nhập để lưu DB.")
            except Exception as e:
                st.caption(f"Không thể lưu server: {e}")

    with col2:
        if st.button("Test Connection", key="settings_test"):
            import requests

            try:
                # Test via backend health or direct LLM ping (rule-based fallback ensures always ok)
                r = requests.get("http://localhost:8000/health", timeout=5)
                if r.ok:
                    st.success(f"Backend OK: {r.json()}")
                else:
                    st.warning(f"Backend status {r.status_code}")
                # Also test ai_service fallback
                import pandas as pd

                from src.core.ai_service import get_ai_service

                svc = get_ai_service(api_key, provider)
                df = pd.DataFrame({"a": [1, 2, 3]})
                report = svc.generate_report(df, "overview")
                st.caption(f"AI service model_used={report.model_used} (rule-based nếu không key)")
            except Exception as e:
                st.error(f"Test failed: {e}")

    st.divider()
    st.markdown("**Hiện tại session:**")
    st.json(
        {"provider": st.session_state.get("ai_provider", "openai"), "has_key": bool(st.session_state.get("ai_api_key"))}
    )
