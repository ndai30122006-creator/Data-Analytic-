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
    
    tab1, tab2 = st.tabs(["Đăng nhập", "Đăng ký"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Nhập username")
            password = st.text_input("Password", type="password", placeholder="Nhập password")
            submit = st.form_submit_button("Đăng nhập", use_container_width=True)
            
            if submit:
                # Simple authentication (in production, use database)
                users = load_users()
                
                if username in users and hash_password(password) == users[username]:
                    st.session_state.authenticated = True
                    st.session_state.username = username
                    st.success(f"✅ Đăng nhập thành công! Xin chào {username}")
                    st.rerun()
                else:
                    st.error("❌ Username hoặc password không đúng")
        
        st.caption("Demo accounts: admin/admin123, user/user123, teacher/teacher123")
    
    with tab2:
        with st.form("register_form"):
            new_username = st.text_input("Username", placeholder="Chọn username", key="reg_user")
            new_password = st.text_input("Password", type="password", placeholder="Chọn password", key="reg_pass")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Nhập lại password", key="reg_confirm")
            register_submit = st.form_submit_button("Đăng ký", use_container_width=True)
            
            if register_submit:
                if not new_username or not new_password:
                    st.error("❌ Vui lòng nhập đầy đủ thông tin")
                elif new_password != confirm_password:
                    st.error("❌ Password không khớp")
                elif len(new_password) < 6:
                    st.error("❌ Password phải có ít nhất 6 ký tự")
                else:
                    users = load_users()
                    if new_username in users:
                        st.error("❌ Username đã tồn tại")
                    else:
                        users[new_username] = hash_password(new_password)
                        save_users(users)
                        st.success(f"✅ Đăng ký thành công! Bạn có thể đăng nhập với {new_username}")
                        st.info("Chuyển sang tab Đăng nhập để đăng nhập")

def logout():
    """Logout user"""
    st.session_state.authenticated = False
    if 'username' in st.session_state:
        del st.session_state.username
    st.rerun()

def load_users():
    """Load users from file"""
    import json
    import os
    users_file = "users.json"
    
    # Default users
    default_users = {
        "admin": hash_password("admin123"),
        "user": hash_password("user123"),
        "teacher": hash_password("teacher123")
    }
    
    if os.path.exists(users_file):
        try:
            with open(users_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return default_users
    else:
        # Create file with default users
        save_users(default_users)
        return default_users

def save_users(users):
    """Save users to file"""
    import json
    users_file = "users.json"
    try:
        with open(users_file, 'w', encoding='utf-8') as f:
            json.dump(users, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Lỗi lưu users: {e}")

def require_auth():
    """Decorator to require authentication"""
    if not check_auth():
        login_page()
        st.stop()
