"""File upload component"""
import streamlit as st
from core.storage_manager import CloudStorageManager
from config.settings import SUPPORTED_FILE_TYPES


def render_upload_section(storage_manager: CloudStorageManager):
    """Render file upload area"""
    st.markdown("### 📤 Upload Files")
    
    # Upload options
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.info("ℹ️ Upload files to get started. Use the preview feature to analyze files with AI.")
    
    with col2:
        selected_folder = st.selectbox(
            "Upload to Folder",
            options=["Root Directory"] + [f["folder_name"] for f in storage_manager.get_folders()],
            key="upload_folder_select"
        )
    
    # File uploader
    uploaded_files = st.file_uploader(
        "Select files to upload (supports resumable upload)",
        type=SUPPORTED_FILE_TYPES,
        accept_multiple_files=True,
        help="Supports Excel, PDF, images, CSV and other formats, resumable upload enabled by default"
    )
    
    if uploaded_files:
        for uploaded_file in uploaded_files:
            col_name, col_size, col_upload = st.columns([3, 1, 1])
            
            with col_name:
                st.write(f"📄 {uploaded_file.name}")
            
            with col_size:
                st.caption(storage_manager.format_file_size(len(uploaded_file.getbuffer())))
            
            with col_upload:
                if st.button("📤 Upload", key=f"upload_{uploaded_file.name}"):
                    # Get target folder ID
                    target_folder_id = None
                    if selected_folder != "Root Directory":
                        folders = storage_manager.get_folders()
                        for folder in folders:
                            if folder["folder_name"] == selected_folder:
                                target_folder_id = folder["id"]
                                break
                    
                    # Upload with resumable upload (default)
                    with st.spinner(f"Uploading {uploaded_file.name}..."):
                        result = storage_manager.upload_file_with_resume(uploaded_file, target_folder_id)
                        
                        if result["success"]:
                            st.success(f"✅ {uploaded_file.name} uploaded successfully!")
                            
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
                                st.info(f"💡 File uploaded to folder. Switched to folder view.")
                                print(f"[DEBUG] file_upload: Switched to folder_id={target_folder_id}")
                            else:
                                # If uploaded to root, make sure we're viewing root
                                st.session_state.current_folder_id = None
                                print(f"[DEBUG] file_upload: Set current_folder_id to None (root)")
                            
                            # Force refresh
                            print(f"[DEBUG] file_upload: Triggering rerun after upload")
                            st.rerun()
                        else:
                            st.error(f"❌ Upload failed: {result.get('error', 'Unknown error')}")
