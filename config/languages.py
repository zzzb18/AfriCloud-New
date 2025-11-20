"""多语言支持模块 - 英语和斯瓦希里语"""
import streamlit as st

# 翻译字典
TRANSLATIONS = {
    "en": {
        # 通用
        "app_title": "AI Cloud Storage",
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
        "unclassified": "Unclassified",
        
        # 标签页
        "home": "Home",
        "tools": "Tools",
        
        # 文件操作
        "back_to_root": "Back to Root",
        "back_to_file_list": "Back to File List",
        "back_to_categories": "Back to Categories",
        "refresh": "Refresh",
        "view": "View",
        "list": "List",
        "thumbnail": "Thumbnail",
        "create": "Create",
        "created_successfully": "Created successfully!",
        "please_enter_name": "Please enter a name",
        "unknown_error": "Unknown error",
        "total_files": "Total {} files",
        "no_files_yet": "No files yet, click the upload button to start uploading files",
        
        # 文件上传
        "upload_files": "Upload Files",
        "upload_info": "Upload files to get started. Use the preview feature to analyze files with AI.",
        "upload_to_folder": "Upload to Folder",
        "root_directory": "Root Directory",
        "select_files_to_upload": "Select files to upload (supports resumable upload)",
        "upload_help": "Supports Excel, PDF, images, CSV and other formats, resumable upload enabled by default",
        "uploading": "Uploading {}...",
        "uploaded_successfully": "{} uploaded successfully!",
        "upload_failed": "Upload failed: {}",
        "file_uploaded_to_folder": "File uploaded to folder. Switched to folder view.",
        
        # 文件列表
        "cached": "Cached",
        "cloud": "Cloud",
        "deleted_successfully": "Deleted successfully!",
        "more": "More",
        "unknown": "Unknown",
        
        # 文件预览
        "file_preview": "File Preview",
        "file_size_label": "File Size",
        "file_type_label": "File Type",
        "upload_time_label": "Upload Time",
        "status": "Status",
        "pdf_preview": "PDF Preview: {} (Page 1)",
        "pdf_has_pages": "PDF has {} pages, showing page 1",
        "pdf_preview_failed": "PDF preview failed: {}",
        "download_pdf": "Download PDF",
        "pdf_preview_requires": "PDF preview requires PyMuPDF: pip install PyMuPDF",
        "excel_preview": "Excel Preview: {} (Showing first 20 rows, total {} rows)",
        "excel_file_empty": "Excel file is empty",
        "excel_preview_failed": "Excel preview failed: {}",
        "download_excel": "Download Excel",
        "csv_preview": "CSV Preview: {} (Showing first 20 rows, total {} rows)",
        "csv_file_empty": "CSV file is empty",
        "csv_preview_failed": "CSV preview failed: {}",
        "download_csv": "Download CSV",
        "text_preview": "Text Preview: {} (Showing first 5000 characters, total {} characters)",
        "file_content": "File Content",
        "text_preview_failed": "Text preview failed: {}",
        "download_text": "Download Text",
        "preview_not_supported": "Preview not supported for {} file type",
        "download_file": "Download File",
        "unable_to_read_file": "Unable to read file content",
        
        # AI分析
        "ai_intelligent_analysis": "AI Intelligent Analysis",
        "start_ai_analysis": "Start AI Analysis",
        "ai_is_analyzing": "AI is analyzing the file...",
        "ai_analysis_completed": "AI analysis completed!",
        "ai_analysis_failed": "AI analysis failed: {}",
        "analysis_results": "Analysis Results",
        "industry_category": "Industry Category",
        "confidence": "Confidence",
        "analysis_method": "Analysis Method",
        "key_phrases": "Key Phrases:",
        "summary": "Summary: {}",
        
        # AI问答
        "ask_ai": "Ask AI",
        "enter_your_question": "Enter your question",
        "question_placeholder": "e.g., What is the main content of this file? What trends are in the data?",
        "voice_input": "Voice Input",
        "click_to_record": "Click the record button to start recording",
        "auto_transcribing": "Auto transcribing speech...",
        "audio_data_empty": "Audio data is empty, please record again",
        "transcription_successful": "Transcription successful: {}...",
        "speech_recognition_failed": "Speech recognition failed, please try again. If the problem persists, please check:\n1. Network connection (if using online recognition)\n2. Audio quality\n3. Whether necessary dependency libraries are installed",
        "error_processing_audio": "Error processing audio: {}",
        "transcribed": "Transcribed: {}...",
        "ask": "Ask",
        "ai_is_thinking": "AI is thinking...",
        "ai_response_failed": "AI response failed: {}",
        "please_enter_question": "Please enter a question",
        "auto_classify": "Auto Classify",
        "file_moved_to": "File moved to: {}",
        "automatically_switched_to_folder": "Automatically switched to folder: {}",
        "classification_failed": "Classification failed: {}",
        "unable_to_determine_classification": "Unable to determine file classification",
        "please_perform_ai_analysis_first": "Please perform AI analysis first",
        "ai_response": "AI Response",
        
        # 行业分类
        "industry_classification_view": "Industry Classification View",
        "browse_files_by_category": "Browse files organized by agricultural industry categories",
        "view": "View {}",
        "files": "files",
        "view_mode": "View Mode",
        "no_files_in_category": "No files found in {} category",
        "summary_statistics": "Summary Statistics",
        "total_files": "Total Files",
        "categories": "Categories",
        
        # 工具页面
        "use_tools_in_sidebar": "Use the tools in the sidebar to access various features",
        "select_category_from_sidebar": "Select a category from the sidebar to view files by industry",
        
        # 语言选择器
        "language": "Language",
        "lugha": "Lugha",
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
        "unclassified": "Haijasajiliwa",
        
        # 标签页
        "home": "Nyumbani",
        "tools": "Zana",
        
        # 文件操作
        "back_to_root": "Rudi kwenye Mzizi",
        "back_to_file_list": "Rudi kwenye Orodha ya Faili",
        "back_to_categories": "Rudi kwenye Kategoria",
        "refresh": "Onyesha Upya",
        "view": "Angalia",
        "list": "Orodha",
        "thumbnail": "Kidogo",
        "create": "Unda",
        "created_successfully": "Imeundwa kwa mafanikio!",
        "please_enter_name": "Tafadhali ingiza jina",
        "unknown_error": "Hitilafu isiyojulikana",
        "total_files": "Jumla ya faili {}",
        "no_files_yet": "Hakuna faili bado, bofya kitufe cha kupakia ili kuanza kupakia faili",
        
        # 文件上传
        "upload_files": "Pakia Faili",
        "upload_info": "Pakia faili ili kuanza. Tumia kipengele cha kuonyesha awali ili kuchambua faili na AI.",
        "upload_to_folder": "Pakia kwenye Folda",
        "root_directory": "Msingi wa Folda",
        "select_files_to_upload": "Chagua faili za kupakia (inasaidia kupakia tena)",
        "upload_help": "Inasaidia Excel, PDF, picha, CSV na aina nyingine za faili, kupakia tena kimewezeshwa kwa default",
        "uploading": "Inapakia {}...",
        "uploaded_successfully": "{} imepakiwa kwa mafanikio!",
        "upload_failed": "Kupakia kumeshindwa: {}",
        "file_uploaded_to_folder": "Faili imepakiwa kwenye folda. Imebadilishwa kwenye muonekano wa folda.",
        
        # 文件列表
        "cached": "Imehifadhiwa",
        "cloud": "Wingu",
        "deleted_successfully": "Imefutwa kwa mafanikio!",
        "more": "Zaidi",
        "unknown": "Haijulikani",
        
        # 文件预览
        "file_preview": "Onyesho la Awali la Faili",
        "file_size_label": "Ukubwa wa Faili",
        "file_type_label": "Aina ya Faili",
        "upload_time_label": "Muda wa Kupakia",
        "status": "Hali",
        "pdf_preview": "Onyesho la Awali la PDF: {} (Ukurasa 1)",
        "pdf_has_pages": "PDF ina kurasa {}, inaonyesha ukurasa 1",
        "pdf_preview_failed": "Onyesho la awali la PDF limeshindwa: {}",
        "download_pdf": "Pakua PDF",
        "pdf_preview_requires": "Onyesho la awali la PDF linahitaji PyMuPDF: pip install PyMuPDF",
        "excel_preview": "Onyesho la Awali la Excel: {} (Inaonyesha safu 20 za kwanza, jumla ya safu {})",
        "excel_file_empty": "Faili ya Excel ni tupu",
        "excel_preview_failed": "Onyesho la awali la Excel limeshindwa: {}",
        "download_excel": "Pakua Excel",
        "csv_preview": "Onyesho la Awali la CSV: {} (Inaonyesha safu 20 za kwanza, jumla ya safu {})",
        "csv_file_empty": "Faili ya CSV ni tupu",
        "csv_preview_failed": "Onyesho la awali la CSV limeshindwa: {}",
        "download_csv": "Pakua CSV",
        "text_preview": "Onyesho la Awali la Maandishi: {} (Inaonyesha herufi 5000 za kwanza, jumla ya herufi {})",
        "file_content": "Maudhui ya Faili",
        "text_preview_failed": "Onyesho la awali la maandishi limeshindwa: {}",
        "download_text": "Pakua Maandishi",
        "preview_not_supported": "Onyesho la awali halisaidii aina ya faili {}",
        "download_file": "Pakua Faili",
        "unable_to_read_file": "Haiwezi kusoma maudhui ya faili",
        
        # AI分析
        "ai_intelligent_analysis": "Uchambuzi wa Akili wa AI",
        "start_ai_analysis": "Anza Uchambuzi wa AI",
        "ai_is_analyzing": "AI inachambua faili...",
        "ai_analysis_completed": "Uchambuzi wa AI umekamilika!",
        "ai_analysis_failed": "Uchambuzi wa AI umeshindwa: {}",
        "analysis_results": "Matokeo ya Uchambuzi",
        "industry_category": "Kategoria ya Sekta",
        "confidence": "Kujiamini",
        "analysis_method": "Njia ya Uchambuzi",
        "key_phrases": "Maneno Muhimu:",
        "summary": "Muhtasari: {}",
        
        # AI问答
        "ask_ai": "Uliza AI",
        "enter_your_question": "Ingiza swali lako",
        "question_placeholder": "mfano, Ni nini maudhui makuu ya faili hii? Ni mienendo gani katika data?",
        "voice_input": "Ingizo la Sauti",
        "click_to_record": "Bofya kitufe cha kurekodi ili kuanza kurekodi",
        "auto_transcribing": "Inatafsiri sauti moja kwa moja...",
        "audio_data_empty": "Data ya sauti ni tupu, tafadhali rekodi tena",
        "transcription_successful": "Utafsiri umefanikiwa: {}...",
        "speech_recognition_failed": "Utambuzi wa sauti umeshindwa, tafadhali jaribu tena. Ikiwa shida inaendelea, tafadhali angalia:\n1. Muunganisho wa mtandao (ikiwa unatumia utambuzi wa mtandao)\n2. Ubora wa sauti\n3. Ikiwa maktaba za msaidizi zinahitajika zimewekwa",
        "error_processing_audio": "Hitilafu katika kuchakata sauti: {}",
        "transcribed": "Imetafsiriwa: {}...",
        "ask": "Uliza",
        "ai_is_thinking": "AI inafikiria...",
        "ai_response_failed": "Jibu la AI limeshindwa: {}",
        "please_enter_question": "Tafadhali ingiza swali",
        "auto_classify": "Sajili Moja kwa Moja",
        "file_moved_to": "Faili imehamishwa kwenda: {}",
        "automatically_switched_to_folder": "Imebadilishwa moja kwa moja kwenye folda: {}",
        "classification_failed": "Usajili umeshindwa: {}",
        "unable_to_determine_classification": "Haiwezi kuamua usajili wa faili",
        "please_perform_ai_analysis_first": "Tafadhali fanya uchambuzi wa AI kwanza",
        "ai_response": "Jibu la AI",
        
        # 行业分类
        "industry_classification_view": "Muonekano wa Usajili wa Sekta",
        "browse_files_by_category": "Vinjari faili zilizopangwa kwa kategoria za sekta ya kilimo",
        "view": "Angalia {}",
        "files": "faili",
        "view_mode": "Hali ya Kuangalia",
        "no_files_in_category": "Hakuna faili zilizopatikana katika kategoria ya {}",
        "summary_statistics": "Takwimu za Muhtasari",
        "total_files": "Jumla ya Faili",
        "categories": "Kategoria",
        
        # 工具页面
        "use_tools_in_sidebar": "Tumia zana kwenye upau wa upande ili kufikia vipengele mbalimbali",
        "select_category_from_sidebar": "Chagua kategoria kutoka upau wa upande ili kuangalia faili kwa sekta",
        
        # 语言选择器
        "language": "Lugha",
        "lugha": "Lugha",
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

