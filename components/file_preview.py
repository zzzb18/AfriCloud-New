"""File preview component"""
import streamlit as st
import pandas as pd
import io
from core.storage_manager import CloudStorageManager
from utils.dependencies import PDF_AVAILABLE, WHISPER_AVAILABLE, SPEECH_RECOGNITION_AVAILABLE
from utils.speech_to_text import transcribe_audio, get_available_methods, check_ffmpeg


def render_file_preview_modal(storage_manager: CloudStorageManager, file_id: int):
    """Render file preview page"""
    # Get file info directly by file_id (not dependent on folder)
    print(f"[DEBUG] file_preview: Attempting to preview file - ID: {file_id}")
    file = storage_manager.get_file_by_id(file_id)
    
    if not file:
        print(f"[DEBUG] file_preview: File not found - ID: {file_id}")
        st.error(f"File not found (ID: {file_id})")
        # 返回按钮
        if st.button("← Back to File List", use_container_width=True):
            st.session_state.viewing_file_id = None
            st.rerun()
        return
    
    print(f"[DEBUG] file_preview: File found - Name: {file.get('filename')}, Path: {file.get('file_path')}")
    
    # 返回按钮
    if st.button("← Back to File List", type="secondary", use_container_width=True):
        st.session_state.viewing_file_id = None
        if f"ai_response_{file_id}" in st.session_state:
            del st.session_state[f"ai_response_{file_id}"]
        st.rerun()
    
    st.markdown("---")
    
    # Preview area
    st.markdown(f"## 📄 {file.get('filename', 'Unknown')}")
    
    # File information
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("File Size", storage_manager.format_file_size(file.get('file_size', 0)))
    with col2:
        st.metric("File Type", file.get('file_type', 'unknown'))
    with col3:
        st.metric("Upload Time", file.get('upload_time', '')[:10] if file.get('upload_time') else '')
    with col4:
        st.metric("Status", "✅ Cached" if file.get('is_cached') else "☁️ Cloud")
    
    st.markdown("---")
    
    # Preview content
    st.markdown("### 👁️ File Preview")
    file_data = storage_manager.preview_file(file_id)
    
    if file_data:
        file_type = file.get('file_type', 'unknown')
        filename = file.get('filename', '')
        
        if file_type == 'image':
            st.image(file_data, caption=filename, use_container_width=True)
        
        elif file_type == 'application' and filename.endswith('.pdf'):
            if PDF_AVAILABLE:
                try:
                    import fitz
                    pdf_stream = io.BytesIO(file_data)
                    doc = fitz.open(stream=pdf_stream, filetype="pdf")
                    
                    if len(doc) > 0:
                        page = doc[0]
                        mat = fitz.Matrix(1.5, 1.5)
                        pix = page.get_pixmap(matrix=mat)
                        img_data = pix.tobytes("png")
                        st.image(img_data, caption=f"PDF Preview: {filename} (Page 1)", use_container_width=True)
                        if len(doc) > 1:
                            st.caption(f"PDF has {len(doc)} pages, showing page 1")
                    doc.close()
                except Exception as e:
                    st.error(f"PDF preview failed: {str(e)}")
                    st.download_button("📥 Download PDF", file_data, filename, key=f"download_pdf_{file_id}")
            else:
                st.info("PDF preview requires PyMuPDF: pip install PyMuPDF")
                st.download_button("📥 Download PDF", file_data, filename, key=f"download_pdf_{file_id}")
        
        elif file_type == 'application' and filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(io.BytesIO(file_data))
                if not df.empty:
                    st.dataframe(df.head(20), use_container_width=True)
                    st.caption(f"Excel Preview: {filename} (Showing first 20 rows, total {len(df)} rows)")
                else:
                    st.warning("Excel file is empty")
            except Exception as e:
                st.error(f"Excel preview failed: {str(e)}")
                st.download_button("📥 Download Excel", file_data, filename, key=f"download_excel_{file_id}")
        
        elif filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(file_data))
                if not df.empty:
                    st.dataframe(df.head(20), use_container_width=True)
                    st.caption(f"CSV Preview: {filename} (Showing first 20 rows, total {len(df)} rows)")
                else:
                    st.warning("CSV file is empty")
            except Exception as e:
                st.error(f"CSV preview failed: {str(e)}")
                st.download_button("📥 Download CSV", file_data, filename, key=f"download_csv_{file_id}")
        
        elif file_type == 'text' or filename.endswith('.txt'):
            try:
                text_content = file_data.decode('utf-8')
                st.text_area("File Content", text_content[:5000], height=300, key=f"text_preview_{file_id}")
                if len(text_content) > 5000:
                    st.caption(f"Text Preview: {filename} (Showing first 5000 characters, total {len(text_content)} characters)")
            except Exception as e:
                st.error(f"Text preview failed: {str(e)}")
                st.download_button("📥 Download Text", file_data, filename, key=f"download_txt_{file_id}")
        
        else:
            st.info(f"Preview not supported for {file_type} file type")
            st.download_button("📥 Download File", file_data, filename, key=f"download_{file_id}")
    else:
        st.error("Unable to read file content")
    
    st.markdown("---")
    
    # AI Analysis area
    st.markdown("### 🤖 AI Intelligent Analysis")
    
    # Perform AI analysis first
    ai_analysis = storage_manager.get_ai_analysis(file_id)
    if not ai_analysis:
        if st.button("🔍 Start AI Analysis", key=f"start_ai_{file_id}"):
            with st.spinner("AI is analyzing the file..."):
                result = storage_manager.analyze_file_with_ai(file_id)
                if result.get("success"):
                    st.success("AI analysis completed!")
                    st.rerun()
                else:
                    st.error(f"AI analysis failed: {result.get('error', 'Unknown error')}")
    else:
        # Display existing analysis results
        st.markdown("#### 📊 Analysis Results")
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Industry Category", ai_analysis.get('industry_category', 'Unclassified'))
            st.metric("Confidence", f"{ai_analysis.get('confidence_score', 0):.2%}")
        with col2:
            st.metric("Analysis Method", ai_analysis.get('method', 'Unknown'))
            if ai_analysis.get('key_phrases'):
                st.markdown("**Key Phrases:**")
                for phrase in ai_analysis['key_phrases'][:5]:
                    st.caption(f"• {phrase}")
        
        if ai_analysis.get('summary'):
            st.info(f"📝 Summary: {ai_analysis['summary']}")
    
    st.markdown("---")
    
    # AI Q&A area
    st.markdown("#### 💬 Ask AI")
    
    # 输入框和麦克风按钮布局
    col_text, col_mic = st.columns([5, 1])
    
    with col_text:
        # 检查是否有转录的文本需要填入
        transcribed_text_key = f"transcribed_text_{file_id}"
        transcribed_value = st.session_state.get(transcribed_text_key, "")
        
        # 构建text_area的参数
        text_area_params = {
            "label": "Enter your question",
            "placeholder": "e.g., What is the main content of this file? What trends are in the data?",
            "height": 100,
            "key": f"ai_question_{file_id}"
        }
        
        # 如果有转录文本，设置value并清除标记
        if transcribed_value:
            text_area_params["value"] = transcribed_value
            # 清除转录文本，避免下次自动填入
            del st.session_state[transcribed_text_key]
        
        user_question = st.text_area(**text_area_params)
    
    with col_mic:
        st.markdown("<br>", unsafe_allow_html=True)  # 垂直对齐
        # 麦克风按钮
        mic_clicked = st.button("🎤", key=f"mic_button_{file_id}", help="语音输入", use_container_width=True)
        
        # 检查是否有可用的语音识别方法
        available_methods = get_available_methods()
        if not available_methods:
            st.caption("⚠️ 需要安装语音识别库")
    
    # 语音录制区域
    if mic_clicked or st.session_state.get(f"show_audio_recorder_{file_id}", False):
        st.session_state[f"show_audio_recorder_{file_id}"] = True
        
        st.markdown("---")
        st.markdown("**🎤 语音输入**")
        
        # 使用Streamlit的音频输入组件
        audio_data = st.audio_input(
            "点击录制按钮开始录音",
            key=f"audio_input_{file_id}"
        )
        
        if audio_data is not None:
            # 显示音频播放器
            st.audio(audio_data, format="audio/wav")
            
            # 检查是否有可用的识别方法
            if len(available_methods) == 0:
                # 没有可用方法时显示提示
                st.warning("⚠️ 没有可用的语音识别方法")
                if WHISPER_AVAILABLE and not check_ffmpeg():
                    st.info("💡 请安装ffmpeg以使用Whisper，或安装speech_recognition库")
                elif not WHISPER_AVAILABLE and not SPEECH_RECOGNITION_AVAILABLE:
                    st.info("💡 请安装语音识别库：`pip install openai-whisper SpeechRecognition`")
            else:
                # 转文字按钮（自动选择最佳方法）
                if st.button("🔄 转换为文字", key=f"transcribe_{file_id}", type="primary", use_container_width=True):
                    with st.spinner("正在识别语音..."):
                        # 获取音频字节数据（Streamlit的audio_input返回BytesIO）
                        if hasattr(audio_data, 'read'):
                            # 重置到开头
                            audio_data.seek(0)
                            audio_bytes = audio_data.read()
                        else:
                            audio_bytes = audio_data
                        
                        # 自动选择最佳方法进行识别（无需用户选择）
                        transcribed_text = transcribe_audio(audio_bytes)
                        
                        if transcribed_text:
                            # 将识别结果存储到单独的key中，然后通过rerun更新text_area
                            st.session_state[f"transcribed_text_{file_id}"] = transcribed_text
                            st.success(f"✅ 识别成功")
                            st.session_state[f"show_audio_recorder_{file_id}"] = False
                            st.rerun()
                        else:
                            st.error("❌ 语音识别失败，请重试")
        
        # 关闭录音区域按钮
        if st.button("❌ 关闭", key=f"close_recorder_{file_id}"):
            st.session_state[f"show_audio_recorder_{file_id}"] = False
            st.rerun()
        
        st.markdown("---")
    
    col_ask, col_auto = st.columns([3, 1])
    with col_ask:
        if st.button("🚀 Ask", key=f"ask_ai_{file_id}", type="primary", use_container_width=True):
            if user_question:
                with st.spinner("🤔 AI is thinking..."):
                    result = storage_manager.generate_ai_report(file_id, user_question)
                    if result.get("success"):
                        st.session_state[f"ai_response_{file_id}"] = result.get("response", "")
                        st.rerun()
                    else:
                        st.error(f"AI response failed: {result.get('error', 'Unknown error')}")
            else:
                st.warning("Please enter a question")
    
    with col_auto:
        if st.button("📁 Auto Classify", key=f"auto_classify_{file_id}", use_container_width=True):
            if ai_analysis:
                category = ai_analysis.get('industry_category', 'Unclassified')
                if category != "Unclassified":
                    result = storage_manager.move_file_to_industry_folder(file_id, category)
                    if result.get("success"):
                        folder_id = result.get("folder_id")
                        st.success(f"✅ File moved to: {category}")
                        # Automatically switch to the corresponding folder
                        if folder_id:
                            st.session_state.current_folder_id = folder_id
                            st.info(f"💡 Automatically switched to folder: {category}")
                        st.rerun()
                    else:
                        error_msg = result.get("error", "Unknown error")
                        st.error(f"❌ Classification failed: {error_msg}")
                else:
                    st.warning("Unable to determine file classification")
            else:
                st.warning("Please perform AI analysis first")
    
    # Display AI response
    if st.session_state.get(f"ai_response_{file_id}"):
        st.markdown("---")
        st.markdown("#### 🤖 AI Response")
        st.markdown(st.session_state[f"ai_response_{file_id}"])
    
    # 底部返回按钮（可选，顶部已有）
    st.markdown("---")
    if st.button("← Back to File List", key=f"back_to_list_{file_id}", use_container_width=True, type="secondary"):
        st.session_state.viewing_file_id = None
        if f"ai_response_{file_id}" in st.session_state:
            del st.session_state[f"ai_response_{file_id}"]
        st.rerun()
