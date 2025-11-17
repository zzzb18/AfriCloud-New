"""File list component"""
import streamlit as st
import pandas as pd
from core.storage_manager import CloudStorageManager
from typing import List, Dict, Any, Optional


def render_file_list(
    storage_manager: CloudStorageManager,
    files: List[Dict[str, Any]],
    view_mode: str = "list"  # "list" or "thumbnail"
):
    """Render file list
    
    Args:
        storage_manager: Storage manager instance
        files: File list
        view_mode: View mode ("list" or "thumbnail")
    """
    if not files:
        st.info("📁 No files yet, click the upload button to start uploading files")
        return
    
    if view_mode == "list":
        render_list_view(storage_manager, files)
    else:
        render_thumbnail_view(storage_manager, files)


def render_list_view(storage_manager: CloudStorageManager, files: List[Dict[str, Any]]):
    """List view"""
    # Display file list
    for file in files:
        file_id = file['id']
        file_icon = storage_manager.get_file_icon(file.get('file_type', 'unknown'))
        
        # Create column layout
        col1, col2, col3, col4, col5, col6, col7 = st.columns([0.5, 3, 1, 1, 1.5, 1, 1.5])
        
        with col1:
            st.write(file_icon)
        with col2:
            # Clickable filename
            if st.button(f"📄 {file.get('filename', 'Unknown')}", key=f"file_name_{file_id}", use_container_width=True):
                st.session_state.viewing_file_id = file_id
                st.rerun()
        with col3:
            st.caption(storage_manager.format_file_size(file.get('file_size', 0)))
        with col4:
            st.caption(file.get('file_type', 'unknown'))
        with col5:
            upload_time = file.get('upload_time', '')
            st.caption(upload_time[:10] if upload_time else '')
        with col6:
            st.caption("✅ Cached" if file.get('is_cached') else "☁️ Cloud")
        with col7:
            col_del, col_more = st.columns(2)
            with col_del:
                if st.button("🗑️", key=f"del_{file_id}", help="Delete"):
                    result = storage_manager.delete_file(file_id)
                    if result["success"]:
                        st.success("Deleted successfully!")
                        st.rerun()
            with col_more:
                if st.button("⚙️", key=f"more_{file_id}", help="More"):
                    st.session_state[f"show_menu_{file_id}"] = True
        
        st.divider()


def render_thumbnail_view(storage_manager: CloudStorageManager, files: List[Dict[str, Any]]):
    """Thumbnail view"""
    # Display 4 files per row
    cols_per_row = 4
    for i in range(0, len(files), cols_per_row):
        cols = st.columns(cols_per_row)
        for j, col in enumerate(cols):
            if i + j < len(files):
                file = files[i + j]
                with col:
                    file_icon = storage_manager.get_file_icon(file.get('file_type', 'unknown'))
                    filename = file.get('filename', 'Unknown')
                    
                    # File card container
                    with st.container():
                        # File icon and name
                        st.markdown(f"""
                        <div style="
                            background: white;
                            border: 1px solid #e8e8e8;
                            border-radius: 8px;
                            padding: 16px;
                            text-align: center;
                            margin-bottom: 8px;
                        ">
                            <div style="font-size: 48px; margin-bottom: 8px;">{file_icon}</div>
                            <div style="font-size: 12px; color: #333; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">
                                {filename[:20] + '...' if len(filename) > 20 else filename}
                            </div>
                            <div style="font-size: 10px; color: #999; margin-top: 4px;">
                                {storage_manager.format_file_size(file.get('file_size', 0))}
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                        
                        # Preview button
                        if st.button("👁️ Preview", key=f"thumb_preview_{file['id']}", use_container_width=True):
                            st.session_state.viewing_file_id = file['id']
                            st.rerun()
                        
                        # Action buttons
                        col_del, col_more = st.columns(2)
                        with col_del:
                            if st.button("🗑️", key=f"thumb_del_{file['id']}"):
                                result = storage_manager.delete_file(file['id'])
                                if result["success"]:
                                    st.rerun()
                        with col_more:
                            if st.button("⚙️", key=f"thumb_more_{file['id']}"):
                                st.session_state[f"show_menu_{file['id']}"] = True
