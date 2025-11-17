"""语音转文字工具模块"""
import streamlit as st
import io
import tempfile
import os
from typing import Optional

# 检查语音识别库是否可用
try:
    import speech_recognition as sr
    SPEECH_RECOGNITION_AVAILABLE = True
except ImportError:
    SPEECH_RECOGNITION_AVAILABLE = False

# 检查whisper是否可用
try:
    import whisper
    WHISPER_AVAILABLE = True
except ImportError:
    WHISPER_AVAILABLE = False


def transcribe_audio(audio_data: bytes, method: str = "whisper") -> Optional[str]:
    """
    将音频数据转换为文字
    
    Args:
        audio_data: 音频文件的字节数据
        method: 识别方法 ("whisper" 或 "speech_recognition")
    
    Returns:
        识别出的文字，失败返回None
    """
    if method == "whisper" and WHISPER_AVAILABLE:
        return _transcribe_with_whisper(audio_data)
    elif method == "speech_recognition" and SPEECH_RECOGNITION_AVAILABLE:
        return _transcribe_with_speech_recognition(audio_data)
    else:
        st.error("语音识别功能不可用，请安装相关依赖库")
        return None


def _transcribe_with_whisper(audio_data: bytes) -> Optional[str]:
    """使用Whisper模型进行语音转文字"""
    try:
        # 加载模型（使用base模型，较小且速度快）
        if 'whisper_model' not in st.session_state:
            with st.spinner("🔄 正在加载Whisper模型..."):
                st.session_state.whisper_model = whisper.load_model("base")
        
        # 将音频数据保存到临时文件
        # 如果audio_data是BytesIO对象，需要先读取
        if hasattr(audio_data, 'read'):
            audio_bytes = audio_data.read()
        else:
            audio_bytes = audio_data
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(audio_bytes)
            tmp_path = tmp_file.name
        
        try:
            # 使用whisper进行转录
            result = st.session_state.whisper_model.transcribe(tmp_path, language="zh")
            return result["text"]
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except Exception as e:
        st.error(f"Whisper转录失败: {str(e)}")
        return None


def _transcribe_with_speech_recognition(audio_data: bytes) -> Optional[str]:
    """使用speech_recognition库进行语音转文字"""
    try:
        recognizer = sr.Recognizer()
        
        # 将字节数据转换为AudioData对象
        audio_file = io.BytesIO(audio_data)
        with sr.AudioFile(audio_file) as source:
            audio = recognizer.record(source)
        
        # 尝试使用Google Speech Recognition（免费，需要网络）
        try:
            text = recognizer.recognize_google(audio, language="zh-CN")
            return text
        except sr.UnknownValueError:
            st.error("无法识别音频内容")
            return None
        except sr.RequestError as e:
            st.error(f"语音识别服务错误: {str(e)}")
            # 尝试使用离线识别（如果可用）
            try:
                # 使用sphinx作为离线备选（需要安装pocketsphinx）
                text = recognizer.recognize_sphinx(audio, language="zh-CN")
                return text
            except:
                return None
    except Exception as e:
        st.error(f"语音识别失败: {str(e)}")
        return None


def get_available_methods() -> list:
    """获取可用的语音识别方法"""
    methods = []
    if WHISPER_AVAILABLE:
        methods.append("whisper")
    if SPEECH_RECOGNITION_AVAILABLE:
        methods.append("speech_recognition")
    return methods

