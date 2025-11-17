"""Main application file - New UI design"""
import streamlit as st
import pandas as pd
from core.storage_manager import CloudStorageManager
from core.auth import AuthManager
from config.styles import CSS_STYLES
from config.settings import PAGE_CONFIG
from utils.dependencies import PDF_AVAILABLE
from components.sidebar import render_file_type_sidebar, render_tools_sidebar
from components.file_list import render_file_list
from components.file_upload import render_upload_section
from components.file_preview import render_file_preview_modal
from components.industry_view import render_industry_view, render_industry_view_sidebar
from components.login import render_login_page, render_user_info

# Try to import fitz (PDF support)
try:
    import fitz
except ImportError:
    fitz = None

# Page configuration
st.set_page_config(**PAGE_CONFIG)

# Application styles
st.markdown(CSS_STYLES, unsafe_allow_html=True)

# Initialize authentication manager
if 'auth_manager' not in st.session_state:
    st.session_state.auth_manager = AuthManager()

auth_manager = st.session_state.auth_manager

# Check authentication
is_authenticated = False
if 'session_token' in st.session_state:
    user_info = auth_manager.verify_session(st.session_state.session_token)
    if user_info:
        is_authenticated = True
        st.session_state.user_id = user_info['user_id']
        st.session_state.username = user_info['username']
        st.session_state.email = user_info.get('email', '')
    else:
        # Session expired or invalid
        for key in ['session_token', 'user_id', 'username', 'email']:
            if key in st.session_state:
                del st.session_state[key]

# Show login page if not authenticated
if not is_authenticated:
    render_login_page(auth_manager)
    st.stop()

# Initialize cloud storage manager (only if authenticated)
if 'storage_manager' not in st.session_state:
    st.session_state.storage_manager = CloudStorageManager()

storage_manager = st.session_state.storage_manager

# Initialize session state
if 'current_tab' not in st.session_state:
    st.session_state.current_tab = "Home"

if 'view_mode' not in st.session_state:
    st.session_state.view_mode = "list"  # "list" or "thumbnail"

if 'selected_file_type' not in st.session_state:
    st.session_state.selected_file_type = None

if 'current_folder_id' not in st.session_state:
    st.session_state.current_folder_id = None

if 'show_new_folder_dialog' not in st.session_state:
    st.session_state.show_new_folder_dialog = False

if 'selected_industry_category' not in st.session_state:
    st.session_state.selected_industry_category = None

# 页面状态：文件列表页或文件详情页
if 'viewing_file_id' not in st.session_state:
    st.session_state.viewing_file_id = None

# ==================== Left Sidebar Tabs ====================
with st.sidebar:
    st.markdown("""
    <div style="padding: 16px 0; border-bottom: 1px solid #e8e8e8; margin-bottom: 20px;">
        <h2 style="margin: 0; color: #1e293b; font-size: 18px; font-weight: 600;">🌾 AI Cloud Storage</h2>
        <p style="margin: 4px 0 0 0; color: #64748b; font-size: 12px;">Intelligent File Management Platform</p>
    </div>
    """, unsafe_allow_html=True)

    # User info
    render_user_info(auth_manager)

    # Tab selection using buttons instead of st.tabs to better control content visibility
    # This allows us to explicitly track which tab is active
    
    # Tab buttons
    col_home, col_industry, col_tools = st.columns(3)
    
    with col_home:
        if st.button("🏠 Home", key="tab_home", use_container_width=True, 
                     type="primary" if st.session_state.get('current_tab') == "Home" else "secondary"):
            st.session_state.current_tab = "Home"
            st.session_state.selected_industry_category = None  # Clear industry category when switching to Home
            st.rerun()
    
    with col_industry:
        if st.button("📊 Industry View", key="tab_industry", use_container_width=True,
                     type="primary" if st.session_state.get('current_tab') == "Industry View" else "secondary"):
            st.session_state.current_tab = "Industry View"
            st.rerun()
    
    with col_tools:
        if st.button("🛠️ Tools", key="tab_tools", use_container_width=True,
                     type="primary" if st.session_state.get('current_tab') == "Tools" else "secondary"):
            st.session_state.current_tab = "Tools"
            st.session_state.selected_industry_category = None  # Clear industry category when switching to Tools
            st.rerun()
    
    st.markdown("---")

    # Render sidebar content based on current tab
    current_tab = st.session_state.get('current_tab', 'Home')
    
    if current_tab == "Home":
        # File type classification sidebar
        selected_file_type = render_file_type_sidebar(storage_manager)
        st.session_state.selected_file_type = selected_file_type
        
        # Return to root directory button
        if st.session_state.current_folder_id:
            if st.button("🏠 Back to Root", use_container_width=True):
                st.session_state.current_folder_id = None
                st.rerun()
    
    elif current_tab == "Industry View":
        # Industry view sidebar
        render_industry_view_sidebar(storage_manager)
    
    elif current_tab == "Tools":
        # Tools sidebar
        render_tools_sidebar(storage_manager)

# ==================== Main Content Area ====================
# 检查是否在查看文件详情页
viewing_file_id = st.session_state.get('viewing_file_id')

# 只在文件列表页显示顶部操作栏
if not viewing_file_id:
    # Top action bar - cloud storage style
    col_upload, col_new_folder, col_sep1, col_view, col_refresh = st.columns([2, 1.5, 0.2, 1, 1])

    with col_upload:
        if st.button("↑ Upload", type="primary", use_container_width=True):
            st.session_state.show_upload = not st.session_state.get('show_upload', False)

    with col_new_folder:
        # New folder button - using popover for instant creation
        with st.popover("📁 New Folder", help="Create a new folder", use_container_width=True):
            folder_name = st.text_input("Folder Name", placeholder="Enter folder name", key="popover_folder_name")
            col_ok, col_cancel = st.columns(2)
            with col_ok:
                if st.button("Create", type="primary", use_container_width=True, key="popover_create"):
                    if folder_name:
                        result = storage_manager.create_folder(folder_name, st.session_state.current_folder_id)
                        if result["success"]:
                            st.success(f"✅ Created successfully!") 
                            st.rerun()
                        else:
                            st.error(f"❌ {result.get('error', 'Unknown error')}")
                    else:
                        st.warning("Please enter a name")
            with col_cancel:
                if st.button("Cancel", use_container_width=True, key="popover_cancel"):
                    pass

    with col_sep1:
        st.markdown("<div style='color: #ddd;'>|</div>", unsafe_allow_html=True)  # Separator

    with col_view:
        view_mode = st.radio(
            "View",
            options=["List", "Thumbnail"],
        horizontal=True,
            key="view_mode_selector",
            label_visibility="collapsed"
        )
        st.session_state.view_mode = "list" if view_mode == "List" else "thumbnail"

    with col_refresh:
        if st.button("🔄 Refresh", use_container_width=True):
            st.rerun()

    st.markdown("---")

# Main content based on selected tab
current_tab = st.session_state.get('current_tab', 'Home')

# Render content based on current tab and page state
if viewing_file_id:
    # 文件详情页
    render_file_preview_modal(storage_manager, viewing_file_id)
elif current_tab == "Industry View":
    # Industry view content
    if st.session_state.get('selected_industry_category'):
        render_industry_view(storage_manager)
    else:
        st.info("📊 Select a category from the sidebar to view files by industry")
elif current_tab == "Tools":
    # Tools content
    st.markdown("### 🛠️ Tools")
    st.info("Use the tools in the sidebar to access various features")
else:
    # Home tab (default) - show upload area and file list
    # Upload area (collapsible)
    if st.session_state.get('show_upload', False):
        with st.expander("📤 Upload Files", expanded=True):
            render_upload_section(storage_manager)
        st.markdown("---")
    
    # File list area
    st.markdown("### 📁 File List")

    # Get files in current folder
    current_folder_id = st.session_state.current_folder_id
    files = storage_manager.get_files(current_folder_id)

    print(f"[DEBUG] app.py: current_folder_id={current_folder_id}, selected_file_type={st.session_state.get('selected_file_type')}, files_count={len(files)}")
    if files:
        print(f"[DEBUG] app.py: Sample files - {[(f['id'], f['filename'], f['file_type']) for f in files[:3]]}")
    else:
        print(f"[DEBUG] app.py: No files found! Checking database...")
        # Debug: Check if files exist in database
        import sqlite3
        conn = sqlite3.connect(storage_manager.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM files WHERE folder_id IS NULL')
        total_count = cursor.fetchone()[0]
        print(f"[DEBUG] app.py: Total files in database (folder_id IS NULL): {total_count}")
        conn.close()

    # Filter by file type (only if a filter is selected)
    if st.session_state.get('selected_file_type'):
        print(f"[DEBUG] app.py: Filtering by file type: {st.session_state.selected_file_type}")
        filtered_files = []
        for file in files:
            file_type = file.get('file_type', 'unknown')
            filename = file.get('filename', '')
            
            if st.session_state.selected_file_type == 'image' and file_type == 'image':
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'application' and file_type == 'application':
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'excel' and filename.endswith(('.xlsx', '.xls', '.csv')):
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'text' and file_type == 'text':
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'video' and file_type == 'video':
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'audio' and file_type == 'audio':
                filtered_files.append(file)
            elif st.session_state.selected_file_type == 'unknown' and file_type == 'unknown':
                filtered_files.append(file)
        
        print(f"[DEBUG] app.py: After filtering: {len(filtered_files)} files")
        files = filtered_files

    # Display file list
    if files:
        render_file_list(storage_manager, files, st.session_state.view_mode)
    else:
        st.info("📁 No files yet, click the upload button to start uploading files")

    # Bottom information
    st.markdown("---")
    st.caption(f"💾 Total {len(files)} files")
