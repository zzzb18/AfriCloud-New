"""Login and registration components"""
import streamlit as st
from core.auth import AuthManager
from config.languages import get_text


def render_login_page(auth_manager: AuthManager):
    """Render login page"""
    st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="color: #1e293b; margin-bottom: 10px;">{}</h1>
        <p style="color: #64748b; font-size: 16px;">{}</p>
    </div>
    """.format(get_text("app_title"), get_text("app_subtitle")), unsafe_allow_html=True)
    
    # Login/Register tabs
    tab1, tab2 = st.tabs([f"🔐 {get_text('login')}", f"📝 {get_text('register')}"])
    
    with tab1:
        st.markdown(f"### {get_text('login_title')}")
        
        with st.form("login_form"):
            username = st.text_input(get_text("username"), placeholder=get_text("enter_username"))
            password = st.text_input(get_text("password"), type="password", placeholder=get_text("enter_password"))
            
            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.form_submit_button(get_text("login"), type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button(get_text("clear"), use_container_width=True):
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
                        
                        st.success(get_text("welcome_back").format(result['username']))
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', get_text('login_failed'))}")
                else:
                    st.warning(get_text("please_enter_username_password"))
    
    with tab2:
        st.markdown(f"### {get_text('register_title')}")
        
        with st.form("register_form"):
            username = st.text_input(get_text("username"), placeholder=get_text("enter_username"), key="reg_username")
            password = st.text_input(get_text("password"), type="password", placeholder=get_text("enter_password"), key="reg_password")
            confirm_password = st.text_input("Confirm Password", type="password", placeholder="Confirm your password", key="reg_confirm_password")
            email = st.text_input(f"{get_text('email')} (Optional)", placeholder="your.email@example.com", key="reg_email")
            
            col1, col2 = st.columns([1, 1])
            with col1:
                register_button = st.form_submit_button(get_text("register"), type="primary", use_container_width=True)
            with col2:
                if st.form_submit_button(get_text("clear"), use_container_width=True):
                    st.rerun()
            
            if register_button:
                if not username or not password:
                    st.warning(get_text("please_enter_username_password"))
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
                        
                        st.success(get_text("registration_success"))
                        st.rerun()
                    else:
                        st.error(f"❌ {result.get('error', get_text('registration_failed'))}")


def render_user_info(auth_manager: AuthManager):
    """Render user information in sidebar"""
    if 'username' in st.session_state:
        st.markdown("---")
        st.markdown(f"**👤 {st.session_state.username}**")
        
        if st.button(f"🚪 {get_text('logout')}", use_container_width=True):
            if 'session_token' in st.session_state:
                auth_manager.logout_user(st.session_state.session_token)
            
            # Clear session state
            for key in ['session_token', 'user_id', 'username', 'email']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.rerun()

