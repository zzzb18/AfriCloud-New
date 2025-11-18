"""多语言支持模块 - 英语和斯瓦希里语"""
import streamlit as st

# 翻译字典
TRANSLATIONS = {
    "en": {
        # 通用
        "app_title": "🌾 AI Cloud Storage",
        "app_subtitle": "Intelligent File Management Platform",
        "welcome": "Welcome",
        "logout": "Logout",
        "login": "Login",
        "register": "Register",
        "username": "Username",
        "password": "Password",
        "email": "Email",
        "submit": "Submit",
        "cancel": "Cancel",
        "clear": "Clear",
        "save": "Save",
        "delete": "Delete",
        "edit": "Edit",
        "upload": "Upload",
        "download": "Download",
        "preview": "Preview",
        "search": "Search",
        "filter": "Filter",
        "close": "Close",
        "back": "Back",
        "next": "Next",
        "previous": "Previous",
        "confirm": "Confirm",
        "yes": "Yes",
        "no": "No",
        "loading": "Loading...",
        "error": "Error",
        "success": "Success",
        "warning": "Warning",
        "info": "Info",
        
        # 登录和注册
        "login_title": "Login to your account",
        "register_title": "Create a new account",
        "enter_username": "Enter your username",
        "enter_password": "Enter your password",
        "enter_email": "Enter your email",
        "welcome_back": "Welcome back, {}!",
        "login_failed": "Login failed",
        "registration_success": "Registration successful! Please login.",
        "registration_failed": "Registration failed",
        "please_enter_username_password": "Please enter both username and password",
        "please_enter_all_fields": "Please enter all fields",
        
        # 文件管理
        "my_files": "My Files",
        "upload_file": "Upload File",
        "new_folder": "New Folder",
        "folder_name": "Folder Name",
        "file_name": "File Name",
        "file_size": "File Size",
        "file_type": "File Type",
        "upload_time": "Upload Time",
        "no_files": "No files uploaded yet",
        "upload_file_here": "Upload your files here",
        "drag_drop": "Drag and drop files here, or click to browse",
        "file_uploaded": "File uploaded successfully",
        "file_upload_failed": "File upload failed",
        "file_deleted": "File deleted successfully",
        "file_delete_failed": "File delete failed",
        "file_not_found": "File not found",
        
        # 文件类型
        "images": "Images",
        "documents": "Documents",
        "spreadsheets": "Spreadsheets",
        "videos": "Videos",
        "audio": "Audio",
        "others": "Others",
        
        # 工具
        "tools": "Tools",
        "ai_analysis": "AI Analysis",
        "smart_report": "Smart Report",
        "weather_data": "Weather Data",
        "remote_sensing": "Remote Sensing",
        "calculator": "Calculator",
        
        # AI分析
        "ask_question": "Ask a question about this file",
        "analyzing": "Analyzing...",
        "analysis_complete": "Analysis complete",
        "analysis_failed": "Analysis failed",
        "enter_question": "Enter your question here",
        
        # 语音识别
        "speech_to_text": "Speech to Text",
        "record_audio": "Record Audio",
        "convert_to_text": "Convert to Text",
        "recording": "Recording...",
        "transcribing": "Transcribing...",
        "transcription_complete": "Transcription complete",
        "transcription_failed": "Transcription failed",
        
        # 行业视图
        "industry_view": "Industry View",
        "select_category": "Select Category",
        "crop_production": "Crop Production",
        "livestock": "Livestock",
        "agricultural_supplies": "Agricultural Supplies",
        "agricultural_finance": "Agricultural Finance",
        "supply_chain": "Supply Chain",
        "climate_remote_sensing": "Climate & Remote Sensing",
        "agricultural_iot": "Agricultural IoT",
    },
    "sw": {  # Swahili (斯瓦希里语)
        # 通用
        "app_title": "🌾 AI Cloud Storage",
        "app_subtitle": "Jukwaa la Usimamizi wa Faili za Akili",
        "welcome": "Karibu",
        "logout": "Toka",
        "login": "Ingia",
        "register": "Jisajili",
        "username": "Jina la mtumiaji",
        "password": "Nenosiri",
        "email": "Barua pepe",
        "submit": "Wasilisha",
        "cancel": "Ghairi",
        "clear": "Futa",
        "save": "Hifadhi",
        "delete": "Futa",
        "edit": "Hariri",
        "upload": "Pakia",
        "download": "Pakua",
        "preview": "Onyesha awali",
        "search": "Tafuta",
        "filter": "Chuja",
        "close": "Funga",
        "back": "Rudi",
        "next": "Ifuatayo",
        "previous": "Iliyotangulia",
        "confirm": "Thibitisha",
        "yes": "Ndiyo",
        "no": "Hapana",
        "loading": "Inapakia...",
        "error": "Hitilafu",
        "success": "Mafanikio",
        "warning": "Onyo",
        "info": "Maelezo",
        
        # 登录和注册
        "login_title": "Ingia kwenye akaunti yako",
        "register_title": "Unda akaunti mpya",
        "enter_username": "Ingiza jina la mtumiaji",
        "enter_password": "Ingiza nenosiri",
        "enter_email": "Ingiza barua pepe",
        "welcome_back": "Karibu tena, {}!",
        "login_failed": "Kuingia kushindwa",
        "registration_success": "Usajili umefanikiwa! Tafadhali ingia.",
        "registration_failed": "Usajili umeshindwa",
        "please_enter_username_password": "Tafadhali ingiza jina la mtumiaji na nenosiri",
        "please_enter_all_fields": "Tafadhali ingiza sehemu zote",
        
        # 文件管理
        "my_files": "Faili Zangu",
        "upload_file": "Pakia Faili",
        "new_folder": "Folda Mpya",
        "folder_name": "Jina la Folda",
        "file_name": "Jina la Faili",
        "file_size": "Ukubwa wa Faili",
        "file_type": "Aina ya Faili",
        "upload_time": "Muda wa Kupakia",
        "no_files": "Hakuna faili zilizopakiwa bado",
        "upload_file_here": "Pakia faili zako hapa",
        "drag_drop": "Buruta na uangushe faili hapa, au bofya ili kuvinjari",
        "file_uploaded": "Faili imepakiwa kwa mafanikio",
        "file_upload_failed": "Kupakia faili kumeshindwa",
        "file_deleted": "Faili imefutwa kwa mafanikio",
        "file_delete_failed": "Kufuta faili kumeshindwa",
        "file_not_found": "Faili haijapatikana",
        
        # 文件类型
        "images": "Picha",
        "documents": "Hati",
        "spreadsheets": "Jedwali",
        "videos": "Video",
        "audio": "Sauti",
        "others": "Nyingine",
        
        # 工具
        "tools": "Zana",
        "ai_analysis": "Uchambuzi wa AI",
        "smart_report": "Ripoti ya Akili",
        "weather_data": "Data ya Hali ya Hewa",
        "remote_sensing": "Kuchunguza kwa mbali",
        "calculator": "Kikokotoo",
        
        # AI分析
        "ask_question": "Uliza swali kuhusu faili hii",
        "analyzing": "Inachambua...",
        "analysis_complete": "Uchambuzi umekamilika",
        "analysis_failed": "Uchambuzi umeshindwa",
        "enter_question": "Ingiza swali lako hapa",
        
        # 语音识别
        "speech_to_text": "Sauti kwa Maandishi",
        "record_audio": "Rekodi Sauti",
        "convert_to_text": "Badilisha kuwa Maandishi",
        "recording": "Inarekodi...",
        "transcribing": "Inatafsiri...",
        "transcription_complete": "Utafsiri umekamilika",
        "transcription_failed": "Utafsiri umeshindwa",
        
        # 行业视图
        "industry_view": "Muonekano wa Sekta",
        "select_category": "Chagua Kategoria",
        "crop_production": "Uzalishaji wa Mazao",
        "livestock": "Mifugo",
        "agricultural_supplies": "Vifaa vya Kilimo",
        "agricultural_finance": "Fedha za Kilimo",
        "supply_chain": "Mnyororo wa Usambazaji",
        "climate_remote_sensing": "Hali ya Hewa na Kuchunguza kwa mbali",
        "agricultural_iot": "IoT ya Kilimo",
    }
}


def get_current_language() -> str:
    """获取当前语言"""
    if 'language' not in st.session_state:
        st.session_state.language = 'en'  # 默认英语
    return st.session_state.language


def set_language(language: str):
    """设置语言"""
    if language in TRANSLATIONS:
        st.session_state.language = language
    else:
        st.session_state.language = 'en'  # 默认英语


def get_text(key: str, default: str = None) -> str:
    """
    获取翻译文本
    
    Args:
        key: 翻译键
        default: 如果找不到翻译，返回的默认值
    
    Returns:
        翻译后的文本
    """
    language = get_current_language()
    translations = TRANSLATIONS.get(language, TRANSLATIONS['en'])
    
    # 如果找到翻译，返回翻译
    if key in translations:
        return translations[key]
    
    # 如果找不到，尝试使用英语
    if language != 'en' and key in TRANSLATIONS['en']:
        return TRANSLATIONS['en'][key]
    
    # 如果还是找不到，返回默认值或键本身
    return default if default is not None else key


def get_available_languages() -> list:
    """获取可用语言列表"""
    return list(TRANSLATIONS.keys())


def get_language_name(language_code: str) -> str:
    """获取语言名称"""
    names = {
        'en': 'English',
        'sw': 'Kiswahili'
    }
    return names.get(language_code, language_code)

