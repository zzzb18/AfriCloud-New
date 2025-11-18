"""File upload component"""
import streamlit as st
from core.storage_manager import CloudStorageManager
from config.settings import SUPPORTED_FILE_TYPES
from config.languages import get_text


def render_upload_section(storage_manager: CloudStorageManager):
    """Render file upload area"""
    st.markdown(f"### 📤 {get_text('upload_files')}")
    
    # Upload options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info(f"ℹ️ {get_text('upload_info')}")
    
    with col2:
        selected_folder = st.selectbox(
            get_text("upload_to_folder"),
            options=[get_text("root_directory")] + [f["folder_name"] for f in storage_manager.get_folders()],
            key="upload_folder_select"
        )
    
    # File uploader
    uploaded_files = st.file_uploader(
        get_text("select_files_to_upload"),
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help=get_text("upload_help")
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            col_name, col_size, col_upload = st.columns([3, 1, 1])
            
            with col_name:
                st.write(f"📄 {uploaded_file.name}")
            
            with col_size:
                st.caption(storage_manager.format_file_size(len(uploaded_file.getbuffer())))
            
            with col_upload:
                if st.button(f"📤 {get_text('upload')}", key=f"upload_{uploaded_file.name}"):
                    # Get target folder ID
                    target_folder_id = None
                    if selected_folder != get_text("root_directory"):
                        folders = storage_manager.get_folders()
                        for folder in folders:
                            if folder["folder_name"] == selected_folder:
                                target_folder_id = folder["id"]
                                break
                    
                    # Upload with resumable upload (default)
                    with st.spinner(get_text("uploading").format(uploaded_file.name)):
                        result = storage_manager.upload_file_with_resume(uploaded_file, target_folder_id)
                        
                        if result["success"]:
                            st.success(f"✅ {get_text('uploaded_successfully').format(uploaded_file.name)}")
                            
                            # Clear file type filter to show all files
                            if 'selected_file_type_key' in st.session_state:
                                st.session_state.selected_file_type_key = None
                                print(f"[DEBUG] file_upload: Cleared selected_file_type_key")
                            if 'selected_file_type' in st.session_state:
                                st.session_state.selected_file_type = None
                                print(f"[DEBUG] file_upload: Cleared selected_file_type")
                            
                            # If uploaded to a folder, switch to that folder
                            if target_folder_id:
                                st.session_state.current_folder_id = target_folder_id
                                st.info(f"💡 {get_text('file_uploaded_to_folder')}")
                                print(f"[DEBUG] file_upload: Switched to folder_id={target_folder_id}")
                            else:
                                # If uploaded to root, make sure we're viewing root
                                st.session_state.current_folder_id = None
                                print(f"[DEBUG] file_upload: Set current_folder_id to None (root)")
                            
                            # Force refresh
                            print(f"[DEBUG] file_upload: Triggering rerun after upload")
                            st.rerun()
                        else:
                            st.error(f"❌ {get_text('upload_failed').format(result.get('error', get_text('unknown_error')))}")
