"""Authentication module for Learning Analytics"""
import streamlit as st
import hashlib

def hash_password(password):
    """Hash password for storage"""
    return hashlib.sha256(password.encode()).hexdigest()

def check_auth():
    """Check if user is authenticated"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    return st.session_state.authenticated

def login_page():
    """Render login page"""
    st.markdown("""
    <div class="hero-bg">
        <div class="hero">
            <h1>🎓 Learning Analytics</h1>
            <p>Đăng nhập để tiếp tục</p>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    with st.form("login_form"):
        username = st.text_input("Username", placeholder="Nhập username")
        password = st.text_input("Password", type="password", placeholder="Nhập password")
        submit = st.form_submit_button("Đăng nhập", use_container_width=True)
        
        if submit:
            # Simple authentication (in production, use database)
            users = {
                "admin": hash_password("admin123"),
                "user": hash_password("user123"),
                "teacher": hash_password("teacher123")
            }
            
            if username in users and hash_password(password) == users[username]:
                st.session_state.authenticated = True
                st.session_state.username = username
                st.success(f"✅ Đăng nhập thành công! Xin chào {username}")
                st.rerun()
            else:
                st.error("❌ Username hoặc password không đúng")
    
    st.caption("Demo accounts: admin/admin123, user/user123, teacher/teacher123")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    if 'username' in st.session_state:
        del st.session_state.username
    st.rerun()

def require_auth():
    """Decorator to require authentication"""
    if not check_auth():
        login_page()
        st.stop()