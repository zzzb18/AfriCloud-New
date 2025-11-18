"""语音转文字工具模块"""
import streamlit as st
import io
import tempfile
import os
import shutil
import subprocess
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

# 检查pydub是否可用（用于音频格式转换）
try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False


def check_ffmpeg() -> bool:
    """检查ffmpeg是否可用"""
    return shutil.which("ffmpeg") is not None


def check_ffprobe() -> bool:
    """检查ffprobe是否可用（pydub需要ffprobe）"""
    return shutil.which("ffprobe") is not None


def convert_audio_to_wav(audio_data: bytes, input_format: str = "webm", silent: bool = False) -> Optional[bytes]:
    """
    将音频数据转换为WAV格式
    
    Args:
        audio_data: 原始音频字节数据
        input_format: 输入音频格式（默认webm，Streamlit audio_input的默认格式）
        silent: 是否静默处理错误（不显示警告信息）
    
    Returns:
        转换后的WAV格式字节数据，失败返回None
    """
    # 如果audio_data是BytesIO对象，需要先读取
    if hasattr(audio_data, 'read'):
        audio_bytes = audio_data.read()
        audio_data.seek(0)  # 重置位置
    else:
        audio_bytes = audio_data
    
    # 方法1: 使用pydub转换（如果可用且ffprobe可用）
    if PYDUB_AVAILABLE and check_ffprobe():
        try:
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes), format=input_format)
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            return wav_buffer.getvalue()
        except Exception as e:
            # 静默失败，继续尝试其他方法
            if not silent:
                # 只在调试时显示，正常流程不显示警告
                pass
    
    # 方法2: 使用ffmpeg转换（如果可用，这是最可靠的方法）
    if check_ffmpeg():
        try:
            # 创建临时输入文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=f".{input_format}") as input_file:
                input_file.write(audio_bytes)
                input_path = input_file.name
            
            # 创建临时输出文件
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as output_file:
                output_path = output_file.name
            
            try:
                # 使用ffmpeg转换（静默模式，不显示输出）
                result = subprocess.run(
                    [
                        "ffmpeg", "-y", "-i", input_path,
                        "-ar", "16000",  # 采样率16kHz
                        "-ac", "1",      # 单声道
                        "-f", "wav",
                        output_path
                    ],
                    check=True,
                    capture_output=True,
                    stderr=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL
                )
                
                # 读取转换后的文件
                if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
                    with open(output_path, "rb") as f:
                        wav_data = f.read()
                    return wav_data
            except subprocess.CalledProcessError as e:
                # ffmpeg转换失败
                if not silent:
                    pass  # 静默处理
            except Exception as e:
                if not silent:
                    pass  # 静默处理
            finally:
                # 清理临时文件
                for path in [input_path, output_path]:
                    if os.path.exists(path):
                        try:
                            os.unlink(path)
                        except:
                            pass
        except Exception as e:
            if not silent:
                pass  # 静默处理
    
    # 方法3: 如果输入已经是WAV格式，直接返回
    # 检查是否是WAV格式（WAV文件头以"RIFF"开头）
    if len(audio_bytes) >= 4 and audio_bytes[:4] == b'RIFF':
        return audio_bytes
    
    # 方法4: 尝试使用pydub但不依赖ffprobe（某些格式可能可以）
    if PYDUB_AVAILABLE:
        try:
            # 尝试直接处理，不指定格式（让pydub自动检测）
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_bytes))
            wav_buffer = io.BytesIO()
            audio_segment.export(wav_buffer, format="wav")
            return wav_buffer.getvalue()
        except Exception:
            pass  # 静默失败
    
    # 方法5: 对于Streamlit Cloud环境，如果所有转换都失败，尝试直接使用原始数据
    # 某些情况下，speech_recognition可能能够处理原始格式
    # 或者Streamlit可能已经返回了WAV格式（虽然文档说是WebM）
    if not silent:
        # 只在调试模式下显示提示
        pass
    
    # 如果所有方法都失败，返回None
    return None


def transcribe_audio(audio_data: bytes, method: str = None) -> Optional[str]:
    """
    将音频数据转换为文字（自动选择最佳方法）
    
    Args:
        audio_data: 音频文件的字节数据
        method: 识别方法 ("whisper" 或 "speech_recognition")，如果为None则自动选择
    
    Returns:
        识别出的文字，失败返回None
    """
    # 如果指定了方法，直接使用
    if method:
        if method == "whisper" and WHISPER_AVAILABLE:
            return _transcribe_with_whisper(audio_data)
        elif method == "speech_recognition" and SPEECH_RECOGNITION_AVAILABLE:
            return _transcribe_with_speech_recognition(audio_data)
        else:
            st.error("指定的语音识别方法不可用")
            return None
    
    # 自动选择最佳方法（优先使用Whisper，如果不可用则使用speech_recognition）
    if WHISPER_AVAILABLE and check_ffmpeg():
        # 优先使用Whisper（离线，准确度高）
        result = _transcribe_with_whisper(audio_data)
        if result:
            return result
        # 如果Whisper失败，尝试speech_recognition作为备选
        if SPEECH_RECOGNITION_AVAILABLE:
            return _transcribe_with_speech_recognition(audio_data)
    elif SPEECH_RECOGNITION_AVAILABLE:
        # 如果Whisper不可用，使用speech_recognition
        return _transcribe_with_speech_recognition(audio_data)
    else:
        st.error("语音识别功能不可用，请安装相关依赖库")
        return None
    
    return None


def _transcribe_with_whisper(audio_data: bytes) -> Optional[str]:
    """使用Whisper模型进行语音转文字"""
    # 检查ffmpeg是否可用
    if not check_ffmpeg():
        error_msg = (
            "❌ Whisper需要ffmpeg才能工作。\n\n"
            "请安装ffmpeg：\n"
            "• Streamlit Cloud: 在项目根目录创建 `packages.txt` 文件，添加 `ffmpeg`\n"
            "• Windows: 下载 https://ffmpeg.org/download.html 或使用 `choco install ffmpeg`\n"
            "• macOS: `brew install ffmpeg`\n"
            "• Linux: `sudo apt install ffmpeg` 或 `sudo yum install ffmpeg`\n\n"
            "或者使用 'speech_recognition' 方法（需要网络连接）"
        )
        st.error(error_msg)
        return None
    
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
        
        # 尝试转换音频格式（如果需要，静默模式）
        wav_data = convert_audio_to_wav(audio_bytes, input_format="webm", silent=True)
        if wav_data is None:
            # 如果转换失败，尝试直接使用原始数据
            wav_data = audio_bytes
        
        # 保存到临时文件
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            tmp_file.write(wav_data)
            tmp_path = tmp_file.name
        
        try:
            # 使用whisper进行转录
            result = st.session_state.whisper_model.transcribe(tmp_path, language="zh")
            text = result.get("text", "").strip()
            return text if text else None
        finally:
            # 清理临时文件
            if os.path.exists(tmp_path):
                os.unlink(tmp_path)
    except FileNotFoundError as e:
        if 'ffmpeg' in str(e).lower():
            error_msg = (
                "❌ 找不到ffmpeg。\n\n"
                "请安装ffmpeg：\n"
                "• Streamlit Cloud: 在项目根目录创建 `packages.txt` 文件，添加 `ffmpeg`\n"
                "• Windows: 下载 https://ffmpeg.org/download.html 或使用 `choco install ffmpeg`\n"
                "• macOS: `brew install ffmpeg`\n"
                "• Linux: `sudo apt install ffmpeg` 或 `sudo yum install ffmpeg`\n\n"
                "安装后请重启应用。或者使用 'speech_recognition' 方法（需要网络连接）"
            )
            st.error(error_msg)
        else:
            st.error(f"Whisper转录失败: {str(e)}")
        return None
    except Exception as e:
        error_msg = f"Whisper转录失败: {str(e)}"
        if 'ffmpeg' in str(e).lower():
            error_msg += "\n\n提示：请确保已安装ffmpeg并添加到系统PATH中。"
        st.error(error_msg)
        return None


def _transcribe_with_speech_recognition(audio_data: bytes) -> Optional[str]:
    """使用speech_recognition库进行语音转文字"""
    try:
        recognizer = sr.Recognizer()
        
        # 如果audio_data是BytesIO对象，需要先读取
        if hasattr(audio_data, 'read'):
            audio_bytes = audio_data.read()
            audio_data.seek(0)  # 重置位置
        else:
            audio_bytes = audio_data
        
        # 尝试转换音频格式为WAV（speech_recognition需要WAV格式，静默模式）
        wav_data = convert_audio_to_wav(audio_bytes, input_format="webm", silent=True)
        if wav_data is None:
            # 如果转换失败，尝试直接使用原始数据（可能是WAV格式）
            wav_data = audio_bytes
        
        # 将字节数据转换为AudioData对象
        audio_file = io.BytesIO(wav_data)
        
        try:
            with sr.AudioFile(audio_file) as source:
                # 调整环境噪音（可选，但有助于提高识别准确度）
                recognizer.adjust_for_ambient_noise(source, duration=0.5)
                audio = recognizer.record(source)
        except Exception as e:
            # 如果AudioFile无法读取，可能是格式问题
            error_msg = f"无法读取音频文件: {str(e)}"
            if "could not find codec" in str(e).lower() or "format" in str(e).lower():
                error_msg += "\n\n提示：音频格式转换失败。"
                if not check_ffmpeg():
                    error_msg += "\n请安装ffmpeg以支持音频格式转换："
                    error_msg += "\n• Streamlit Cloud: 在项目根目录创建 `packages.txt` 文件，添加 `ffmpeg`"
                    error_msg += "\n• Windows: 下载 https://ffmpeg.org/download.html 或使用 `choco install ffmpeg`"
                    error_msg += "\n• macOS: `brew install ffmpeg`"
                    error_msg += "\n• Linux: `sudo apt install ffmpeg`"
                elif not check_ffprobe():
                    error_msg += "\nffmpeg已安装，但ffprobe不可用。请确保ffmpeg完整安装（包含ffprobe）。"
            st.error(error_msg)
            return None
        
        # 尝试使用Google Speech Recognition（免费，需要网络）
        try:
            text = recognizer.recognize_google(audio, language="zh-CN")
            return text.strip() if text else None
        except sr.UnknownValueError:
            # 无法识别音频内容（可能是噪音或语言不匹配）
            st.error("无法识别音频内容，请确保：\n1. 录音清晰无噪音\n2. 使用中文语音\n3. 录音时间足够长")
            return None
        except sr.RequestError as e:
            # 网络错误或服务不可用
            error_msg = f"语音识别服务错误: {str(e)}"
            if "network" in str(e).lower() or "connection" in str(e).lower():
                error_msg += "\n\n提示：请检查网络连接，Google Speech Recognition需要网络访问"
            st.error(error_msg)
            
            # 尝试使用离线识别（如果可用）
            try:
                # 使用sphinx作为离线备选（需要安装pocketsphinx）
                text = recognizer.recognize_sphinx(audio, language="zh-CN")
                return text.strip() if text else None
            except Exception:
                return None
    except Exception as e:
        error_msg = f"语音识别失败: {str(e)}"
        # 提供更详细的错误信息
        if "AudioFile" in str(e) or "format" in str(e).lower():
            error_msg += "\n\n提示：音频格式可能不支持。"
            if not check_ffmpeg():
                error_msg += "\n请安装ffmpeg以支持音频格式转换："
                error_msg += "\n• Streamlit Cloud: 在项目根目录创建 `packages.txt` 文件，添加 `ffmpeg`"
                error_msg += "\n• Windows: 下载 https://ffmpeg.org/download.html 或使用 `choco install ffmpeg`"
                error_msg += "\n• macOS: `brew install ffmpeg`"
                error_msg += "\n• Linux: `sudo apt install ffmpeg`"
        st.error(error_msg)
        return None


def get_available_methods() -> list:
    """获取可用的语音识别方法"""
    methods = []
    # 只有whisper可用且ffmpeg可用时才添加whisper
    if WHISPER_AVAILABLE and check_ffmpeg():
        methods.append("whisper")
    elif WHISPER_AVAILABLE and not check_ffmpeg():
        # Whisper可用但ffmpeg不可用，不添加到列表但保留信息
        pass
    if SPEECH_RECOGNITION_AVAILABLE:
        methods.append("speech_recognition")
    return methods


def get_method_info() -> dict:
    """获取各方法的详细信息"""
    info = {}
    if WHISPER_AVAILABLE:
        if check_ffmpeg():
            info["whisper"] = {
                "available": True,
                "description": "Whisper（离线，需要ffmpeg）",
                "status": "✅ 可用"
            }
        else:
            info["whisper"] = {
                "available": False,
                "description": "Whisper（离线，需要ffmpeg）",
                "status": "❌ 需要安装ffmpeg"
            }
    if SPEECH_RECOGNITION_AVAILABLE:
        info["speech_recognition"] = {
            "available": True,
            "description": "SpeechRecognition（在线，需要网络）",
            "status": "✅ 可用"
        }
    return info

