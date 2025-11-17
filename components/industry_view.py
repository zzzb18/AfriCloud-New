"""Industry view component"""
import streamlit as st
from core.storage_manager import CloudStorageManager
from components.file_list import render_file_list
from typing import List, Dict, Any


def render_industry_view(storage_manager: CloudStorageManager):
    """Render industry classification view"""
    
    # Get all industry categories
    categories = get_industry_categories()
    
    # Display category selection
    st.markdown("### 📊 Industry Classification View")
    st.markdown("Browse files organized by agricultural industry categories")
    st.markdown("---")
    
    # Create category cards in a grid layout
    cols = st.columns(3)
    selected_category = None
    
    for idx, category in enumerate(categories):
        col = cols[idx % 3]
        with col:
            # Get file count for this category
            file_count = get_file_count_by_category(storage_manager, category["key"])
            
            # Category card
            card_color = category.get("color", "#e3f2fd")
            with st.container():
                st.markdown(f"""
                <div style="
                    background: {card_color};
                    border: 2px solid #bbdefb;
                    border-radius: 8px;
                    padding: 16px;
                    margin-bottom: 12px;
                    cursor: pointer;
                    transition: transform 0.2s;
                ">
                    <div style="font-size: 32px; margin-bottom: 8px;">{category["icon"]}</div>
                    <div style="font-size: 16px; font-weight: 600; color: #1976d2; margin-bottom: 4px;">
                        {category["name"]}
                    </div>
                    <div style="font-size: 12px; color: #666;">
                        {file_count} files
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button(f"View {category['name']}", key=f"view_category_{category['key']}", use_container_width=True):
                    selected_category = category["key"]
                    st.session_state.selected_industry_category = selected_category
                    st.rerun()
    
    st.markdown("---")
    
    # Display files for selected category
    if st.session_state.get('selected_industry_category'):
        category_key = st.session_state.selected_industry_category
        category_info = next((c for c in categories if c["key"] == category_key), None)
        
        if category_info:
            st.markdown(f"#### {category_info['icon']} {category_info['name']}")
            
            # Back button
            if st.button("← Back to Categories", key="back_to_categories"):
                st.session_state.selected_industry_category = None
                st.rerun()
            
            st.markdown("---")
            
            # Get files for this category
            files = get_files_by_category(storage_manager, category_key)
            
            if files:
                # View mode selector
                view_mode_col, _ = st.columns([1, 4])
                with view_mode_col:
                    view_mode = st.radio(
                        "View Mode",
                        options=["List", "Thumbnail"],
                        horizontal=True,
                        key="industry_view_mode"
                    )
                    view_mode_value = "list" if view_mode == "List" else "thumbnail"
                
                # Display files
                render_file_list(storage_manager, files, view_mode_value)
            else:
                st.info(f"No files found in {category_info['name']} category")
        else:
            st.session_state.selected_industry_category = None
    else:
        # Show summary statistics
        st.markdown("#### 📈 Summary Statistics")
        stats_cols = st.columns(4)
        
        total_files = 0
        for idx, category in enumerate(categories[:4]):
            count = get_file_count_by_category(storage_manager, category["key"])
            total_files += count
            with stats_cols[idx]:
                st.metric(category["name"], count)
        
        if len(categories) > 4:
            with stats_cols[0]:
                st.metric("Total Files", total_files)


def get_industry_categories() -> List[Dict[str, Any]]:
    """Get list of industry categories with metadata"""
    return [
        {
            "key": "Planting",
            "name": "Crop Production",
            "icon": "🌾",
            "color": "#e8f5e9",
            "description": "Crop cultivation, yield, production reports"
        },
        {
            "key": "Livestock",
            "name": "Livestock",
            "icon": "🐄",
            "color": "#fff3e0",
            "description": "Livestock farming, breeding, feed management"
        },
        {
            "key": "Agri-Finance",
            "name": "Agricultural Finance",
            "icon": "💰",
            "color": "#f3e5f5",
            "description": "Financial reports, insurance, cost analysis"
        },
        {
            "key": "SupplyChain-Storage",
            "name": "Supply Chain & Storage",
            "icon": "🚚",
            "color": "#e1f5fe",
            "description": "Logistics, warehousing, cold chain"
        },
        {
            "key": "Climate-RemoteSensing",
            "name": "Climate & Remote Sensing",
            "icon": "🛰️",
            "color": "#e0f2f1",
            "description": "Weather data, NDVI, EVI, satellite imagery"
        },
        {
            "key": "Inputs-Soil",
            "name": "Agricultural Inputs",
            "icon": "🌱",
            "color": "#fff9c4",
            "description": "Fertilizers, soil analysis, agricultural inputs"
        },
        {
            "key": "Agri-IoT",
            "name": "Agricultural IoT",
            "icon": "📡",
            "color": "#fce4ec",
            "description": "Sensors, automation, smart farming"
        },
        {
            "key": "Unclassified",
            "name": "Unclassified",
            "icon": "📦",
            "color": "#f5f5f5",
            "description": "Files that could not be classified"
        }
    ]


def get_file_count_by_category(storage_manager: CloudStorageManager, category_key: str) -> int:
    """Get file count for a specific category"""
    try:
        import sqlite3
        conn_db = sqlite3.connect(storage_manager.db_path)
        cursor = conn_db.cursor()
        
        # Get folder ID for this category
        folder_name = f"AI_{category_key}"
        cursor.execute('SELECT id FROM folders WHERE folder_name = ?', (folder_name,))
        folder_result = cursor.fetchone()
        
        if folder_result:
            folder_id = folder_result[0]
            cursor.execute('SELECT COUNT(*) FROM files WHERE folder_id = ?', (folder_id,))
            count = cursor.fetchone()[0]
        else:
            count = 0
        
        conn_db.close()
        return count
    except Exception as e:
        print(f"[DEBUG] Error getting file count: {str(e)}")
        return 0


def render_industry_view_sidebar(storage_manager: CloudStorageManager):
    """Render sidebar for industry view"""
    st.markdown("#### 📊 Categories")
    categories = [
        {"key": "Planting", "name": "Crop Production", "icon": "🌾"},
        {"key": "Livestock", "name": "Livestock", "icon": "🐄"},
        {"key": "Agri-Finance", "name": "Agricultural Finance", "icon": "💰"},
        {"key": "SupplyChain-Storage", "name": "Supply Chain", "icon": "🚚"},
        {"key": "Climate-RemoteSensing", "name": "Climate & Remote Sensing", "icon": "🛰️"},
        {"key": "Inputs-Soil", "name": "Agricultural Inputs", "icon": "🌱"},
        {"key": "Agri-IoT", "name": "Agricultural IoT", "icon": "📡"},
        {"key": "Unclassified", "name": "Unclassified", "icon": "📦"},
    ]
    
    for category in categories:
        if st.button(f"{category['icon']} {category['name']}", key=f"sidebar_cat_{category['key']}", use_container_width=True):
            st.session_state.selected_industry_category = category['key']
            st.session_state.current_tab = "Industry View"  # Explicitly set tab
            st.rerun()


def get_files_by_category(storage_manager: CloudStorageManager, category_key: str) -> List[Dict[str, Any]]:
    """Get files for a specific category"""
    try:
        import sqlite3
        conn = sqlite3.connect(storage_manager.db_path)
        cursor = conn.cursor()
        
        # Get folder ID for this category
        folder_name = f"AI_{category_key}"
        cursor.execute('SELECT id FROM folders WHERE folder_name = ?', (folder_name,))
        folder_result = cursor.fetchone()
        
        if folder_result:
            folder_id = folder_result[0]
            cursor.execute('''
                SELECT id, filename, file_size, file_type, upload_time, is_cached
                FROM files WHERE folder_id = ?
                ORDER BY upload_time DESC
            ''', (folder_id,))
            
            files = []
            for row in cursor.fetchall():
                files.append({
                    "id": row[0],
                    "filename": row[1],
                    "file_size": row[2],
                    "file_type": row[3],
                    "upload_time": row[4],
                    "is_cached": bool(row[5])
                })
        else:
            files = []
        
        conn.close()
        return files
    except Exception as e:
        print(f"[DEBUG] Error getting files by category: {str(e)}")
        return []

