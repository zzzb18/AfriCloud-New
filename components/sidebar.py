"""Sidebar component"""
import streamlit as st
import pandas as pd
from core.storage_manager import CloudStorageManager
from config.languages import get_text


def render_file_type_sidebar(storage_manager: CloudStorageManager):
    """Render file type classification sidebar - cloud storage style"""
    
    # File type configuration (icon, name, type value)
    file_type_configs = [
        {"icon": "🖼️", "name": get_text("images"), "type": "image", "key": "sidebar_image"},
        {"icon": "📄", "name": get_text("documents"), "type": "application", "key": "sidebar_doc"},
        {"icon": "📊", "name": get_text("spreadsheets"), "type": "excel", "key": "sidebar_excel"},
        {"icon": "🎥", "name": get_text("videos"), "type": "video", "key": "sidebar_video"},
        {"icon": "🎵", "name": get_text("audio"), "type": "audio", "key": "sidebar_audio"},
        {"icon": "📦", "name": get_text("others"), "type": "unknown", "key": "sidebar_other"},
    ]
    
    # Initialize selected file type
    if 'selected_file_type_key' not in st.session_state:
        st.session_state.selected_file_type_key = None
    
    
    # File type list container styles
    st.markdown("""
    <style>
    .file-type-item {
        padding: 10px 16px;
        margin: 2px 0;
        border-radius: 4px;
        cursor: pointer;
        font-size: 14px;
        display: flex;
        align-items: center;
        gap: 8px;
        transition: background 0.2s;
    }
    .file-type-item:hover {
        background: #f5f5f5;
    }
    .file-type-item.selected {
        background: #e3f2fd;
        color: #1976d2;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # All files option
    is_all_selected = st.session_state.selected_file_type_key is None
    if st.button("📁 All Files", key="sidebar_all_files", use_container_width=True, 
                 type="primary" if is_all_selected else "secondary"):
        st.session_state.selected_file_type_key = None
        st.session_state.selected_file_type = None  # Also clear the selected_file_type
        st.session_state.current_tab = "Home"  # Ensure we're in Home tab
        st.rerun()
    
    st.markdown("---")
    
    # File type list
    for config in file_type_configs:
        is_selected = st.session_state.selected_file_type_key == config["key"]
        
        # Use button style, use primary type when selected
        button_type = "primary" if is_selected else "secondary"
        button_label = f"{config['icon']} {config['name']}"
        
        if st.button(button_label, key=config["key"], use_container_width=True, type=button_type):
            st.session_state.selected_file_type_key = config["key"]
            st.session_state.current_tab = "Home"  # Ensure we're in Home tab when filtering
            st.rerun()
    
    # Return selected file type value
    if st.session_state.selected_file_type_key is None:
        return None
    
    # Find corresponding type based on key
    for config in file_type_configs:
        if config["key"] == st.session_state.selected_file_type_key:
            return config["type"]
    
    return None


def render_tools_sidebar(storage_manager: CloudStorageManager):
    """Render tools sidebar"""
    
    # Agribusiness tools
    st.markdown("#### 🌾 Agricultural Tools")
    
    with st.expander("☁️ Weather & Climate", expanded=False):
        col1, col2 = st.columns(2)
        with col1:
            lat = st.number_input("Latitude", value=0.0, step=0.1, key="weather_lat")
        with col2:
            lon = st.number_input("Longitude", value=20.0, step=0.1, key="weather_lon")
        if st.button("Get 7-Day Weather Summary", use_container_width=True):
            with st.spinner("Fetching weather data..."):
                res = storage_manager.fetch_weather_summary(lat, lon)
                if res.get("success"):
                    ws = res["weather"]["summary"]
                    st.success("Weather data updated")
                    st.json({
                        "7-Day Total Rainfall (mm)": ws.get("7d_total_rain_mm"),
                        "Average Max Temp (°C)": ws.get("avg_tmax"),
                        "Average Min Temp (°C)": ws.get("avg_tmin")
                    })
    
    with st.expander("🛰️ Remote Sensing (NDVI/EVI)", expanded=False):
        col1, col2, col3 = st.columns(3)
        with col1:
            rs_lat = st.number_input("Latitude", value=0.0, step=0.1, key="rs_lat")
        with col2:
            rs_lon = st.number_input("Longitude", value=20.0, step=0.1, key="rs_lon")
        with col3:
            rs_days = st.slider("Days", min_value=7, max_value=60, value=30, key="rs_days")
        if st.button("Generate NDVI/EVI Time Series", use_container_width=True):
            with st.spinner("Generating..."):
                res = storage_manager.compute_remote_sensing_stub(rs_lat, rs_lon, rs_days)
                if res.get("success"):
                    st.success("Generated successfully")
                    rs = res["remote_sensing"]
                    if rs.get("dates") and rs.get("ndvi"):
                        st.line_chart(
                            pd.DataFrame({
                                "date": rs["dates"], 
                                "NDVI": rs["ndvi"]
                            }).set_index("date")
                        )
    
    st.markdown("---")
    
    # AI model status
    st.markdown("#### 🔍 AI Model Status")
    if storage_manager.deepseek_api_key:
        st.success("✅ DeepSeek AI (Configured)")
    else:
        st.warning("⚠️ DeepSeek AI (Not Configured)")
    
    if st.button("🔄 Reload AI", use_container_width=True):
        with st.spinner("Reloading AI models..."):
            storage_manager.init_ai_models()
            st.success("✅ AI models reloaded successfully!")
