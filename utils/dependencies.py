"""依赖库检查和导入"""
import streamlit as st

# PDF支持
try:
    import fitz  # PyMuPDF for PDF preview
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False

# AI功能相关库
try:
    import openai
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

# OCR支持 - 仅使用Tesseract OCR（轻量级，避免内存溢出）
TESSERACT_AVAILABLE = False
OCR_AVAILABLE = False

# 检测Tesseract OCR（唯一OCR引擎）
try:
    import pytesseract
    from PIL import Image
    # 测试Tesseract是否可用
    try:
        pytesseract.get_tesseract_version()
        TESSERACT_AVAILABLE = True
        OCR_AVAILABLE = True
        print("[DEBUG] ✅ Tesseract OCR可用（轻量级，内存占用约50-100MB）")
    except Exception as e:
        import platform
        import os
        system = platform.system()
        print(f"[DEBUG] ⚠️ Tesseract未安装或不在PATH中: {str(e)}")
        
        # Windows: 尝试自动检测常见安装路径
        if system == "Windows":
            common_paths = [
                r"C:\Program Files\Tesseract-OCR\tesseract.exe",
                r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
                r"C:\Users\{}\AppData\Local\Programs\Tesseract-OCR\tesseract.exe".format(os.getenv('USERNAME', '')),
            ]
            
            tesseract_found = False
            for path in common_paths:
                if os.path.exists(path):
                    try:
                        pytesseract.pytesseract.tesseract_cmd = path
                        pytesseract.get_tesseract_version()
                        TESSERACT_AVAILABLE = True
                        OCR_AVAILABLE = True
                        print(f"[DEBUG] ✅ 自动检测到Tesseract: {path}")
                        print("[DEBUG] ✅ Tesseract OCR可用（轻量级，内存占用约50-100MB）")
                        tesseract_found = True
                        break
                    except:
                        continue
            
            if not tesseract_found:
                print("[DEBUG] 💡 Windows安装说明:")
                print("[DEBUG]    1. 下载安装: https://github.com/UB-Mannheim/tesseract/wiki")
                print("[DEBUG]    2. 安装时选择中文语言包")
                print("[DEBUG]    3. 添加到系统PATH: C:\\Program Files\\Tesseract-OCR")
                print("[DEBUG]    4. 安装Python依赖: pip install pytesseract Pillow")
                print("[DEBUG]    详细说明请查看: INSTALL_TESSERACT_WINDOWS.md")
                print("[DEBUG]    或运行安装助手: .\\setup_tesseract_windows.ps1")
        elif system == "Linux":
            print("[DEBUG] 💡 Linux安装: sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim")
            print("[DEBUG] 💡 Python依赖: pip install pytesseract Pillow")
        elif system == "Darwin":  # macOS
            print("[DEBUG] 💡 macOS安装: brew install tesseract")
            print("[DEBUG] 💡 Python依赖: pip install pytesseract Pillow")
        else:
            print("[DEBUG] 💡 请安装Tesseract OCR并添加到PATH")
            print("[DEBUG] 💡 Python依赖: pip install pytesseract Pillow")
except ImportError:
    print("[DEBUG] ⚠️ pytesseract未安装")
    print("[DEBUG] 💡 请安装: pip install pytesseract Pillow")

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.cluster import KMeans
    from sklearn.naive_bayes import MultinomialNB
    from sklearn.pipeline import Pipeline
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSequenceClassification
    TRANSFORMERS_AVAILABLE = True
except ImportError:
    TRANSFORMERS_AVAILABLE = False

# 语音识别支持
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False
