"""Login and registration components"""
import streamlit as st
from core.auth import AuthManager


def render_login_page(auth_manager: AuthManager):
    """Render login page"""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="color: #1e293b; margin-bottom: 10px;">🌾 AI Cloud Storage</h1>
        <p style="color: #64748b; font-size: 16px;">Intelligent File Management Platform</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs(["🔐 Login", "📝 Register"])
    
    with tab1:
        st.markdown("### Login to your account")
        
        with st.form("login_form"):
            username = st.text_input("Username", placeholder="Enter your username")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button("Login", type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button("Clear", use_container_width=True):
                    st.rerun()
            
            if login_button:
                if username and password:
                    result = auth_manager.login_user(username, password)
                    if result.get("success"):
                        # Store session in session state
                        st.session_state.session_token = result["session_token"]
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = result["username"]
                        st.session_state.email = result.get("email", "")
                        
                        st.success(f"✅ Welcome back, {result['username']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Login failed')}")
                else:
                    st.warning("Please enter both username and password")
    
    with tab2:
        st.markdown("### Create a new account")
        
        with st.form("register_form"):
            username = st.text_input("Username", placeholder="Choose a username", key="reg_username")
            password = st.text_input("Password", type="password", placeholder="Choose a password (min 6 characters)", key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm_password")
            email = st.text_input("Email (Optional)", placeholder="your.email@example.com", key="reg_email")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                register_button = st.form_submit_button("Register", type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button("Clear", use_container_width=True):
                    st.rerun()
            
            if register_button:
                if not username or not password:
                    st.warning("Please enter username and password")
                elif password != confirm_password:
                    st.error("❌ Passwords do not match")
                elif len(password) < 6:
                    st.error("❌ Password must be at least 6 characters")
                else:
                    result = auth_manager.register_user(username, password, email)
                    if result.get("success"):
                        # 注册成功后自动登录
                        st.session_state.session_token = result["session_token"]
                        st.session_state.user_id = result["user_id"]
                        st.session_state.username = result["username"]
                        st.session_state.email = result.get("email", "")
                        
                        st.success(f"✅ Account created successfully! Welcome, {result['username']}!")
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', 'Registration failed')}")


def render_user_info(auth_manager: AuthManager):
    """Render user information in sidebar"""
    if 'username' in st.session_state:
        st.markdown("---")
        st.markdown(f"**👤 {st.session_state.username}**")
        
        if st.button("🚪 Logout", use_container_width=True):
            if 'session_token' in st.session_state:
                auth_manager.logout_user(st.session_state.session_token)
            
            # Clear session state
            for key in ['session_token', 'user_id', 'username', 'email']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()

