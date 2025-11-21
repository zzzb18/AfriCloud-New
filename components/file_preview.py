"""File preview component"""
import streamlit as st
import pandas as pd
import io
import hashlib
from core.storage_manager import CloudStorageManager
from utils.dependencies import PDF_AVAILABLE, WHISPER_AVAILABLE, SPEECH_RECOGNITION_AVAILABLE
from utils.speech_to_text import transcribe_audio, get_available_methods, check_ffmpeg
from config.languages import get_text


def render_file_preview_modal(storage_manager: CloudStorageManager, file_id: int):
    """Render file preview page"""
    # Get file info directly by file_id (not dependent on folder)
    print(f"[DEBUG] file_preview: Attempting to preview file - ID: {file_id}")
    file = storage_manager.get_file_by_id(file_id)
    
    if not file:
        print(f"[DEBUG] file_preview: File not found - ID: {file_id}")
        st.error(f"{get_text('file_not_found')} (ID: {file_id})")
        # 返回按钮
        if st.button(f"← {get_text('back_to_file_list')}", use_container_width=True):
            st.session_state.viewing_file_id = None
            st.rerun()
        return
    
    print(f"[DEBUG] file_preview: File found - Name: {file.get('filename')}, Path: {file.get('file_path')}")
    
    # 返回按钮
    if st.button(f"← {get_text('back_to_file_list')}", type="secondary", use_container_width=True):
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
        st.metric(get_text("file_size_label"), storage_manager.format_file_size(file.get('file_size', 0)))
    with col2:
        st.metric(get_text("file_type_label"), file.get('file_type', get_text('unknown')))
    with col3:
        st.metric(get_text("upload_time_label"), file.get('upload_time', '')[:10] if file.get('upload_time') else '')
    with col4:
        st.metric(get_text("status"), f"✅ {get_text('cached')}" if file.get('is_cached') else f"☁️ {get_text('cloud')}")
    
    st.markdown("---")
    
    # Preview content
    st.markdown(f"### 👁️ {get_text('file_preview')}")
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
                        st.image(img_data, caption=get_text("pdf_preview").format(filename), use_container_width=True)
                        if len(doc) > 1:
                            st.caption(get_text("pdf_has_pages").format(len(doc)))
                    doc.close()
                except Exception as e:
                    st.error(get_text("pdf_preview_failed").format(str(e)))
                    st.download_button(f"📥 {get_text('download_pdf')}", file_data, filename, key=f"download_pdf_{file_id}")
            else:
                st.info(get_text("pdf_preview_requires"))
                st.download_button(f"📥 {get_text('download_pdf')}", file_data, filename, key=f"download_pdf_{file_id}")
        
        elif file_type == 'application' and filename.endswith(('.xlsx', '.xls')):
            try:
                df = pd.read_excel(io.BytesIO(file_data))
                if not df.empty:
                    st.dataframe(df.head(20), use_container_width=True)
                    st.caption(get_text("excel_preview").format(filename, len(df)))
                else:
                    st.warning(get_text("excel_file_empty"))
            except Exception as e:
                st.error(get_text("excel_preview_failed").format(str(e)))
                st.download_button(f"📥 {get_text('download_excel')}", file_data, filename, key=f"download_excel_{file_id}")
        
        elif filename.endswith('.csv'):
            try:
                df = pd.read_csv(io.BytesIO(file_data))
                if not df.empty:
                    st.dataframe(df.head(20), use_container_width=True)
                    st.caption(get_text("csv_preview").format(filename, len(df)))
                else:
                    st.warning(get_text("csv_file_empty"))
            except Exception as e:
                st.error(get_text("csv_preview_failed").format(str(e)))
                st.download_button(f"📥 {get_text('download_csv')}", file_data, filename, key=f"download_csv_{file_id}")
        
        elif file_type == 'text' or filename.endswith('.txt'):
            try:
                text_content = file_data.decode('utf-8')
                st.text_area(get_text("file_content"), text_content[:5000], height=300, key=f"text_preview_{file_id}")
                if len(text_content) > 5000:
                    st.caption(get_text("text_preview").format(filename, len(text_content)))
            except Exception as e:
                st.error(get_text("text_preview_failed").format(str(e)))
                st.download_button(f"📥 {get_text('download_text')}", file_data, filename, key=f"download_txt_{file_id}")
        
        else:
            st.info(get_text("preview_not_supported").format(file_type))
            st.download_button(f"📥 {get_text('download_file')}", file_data, filename, key=f"download_{file_id}")
    else:
        st.error(get_text("unable_to_read_file"))
    
    st.markdown("---")
    
    # AI Analysis area
    st.markdown(f"### 🤖 {get_text('ai_intelligent_analysis')}")
    
    # Perform AI analysis first
    ai_analysis = storage_manager.get_ai_analysis(file_id)
    if not ai_analysis:
        if st.button(f"🔍 {get_text('start_ai_analysis')}", key=f"start_ai_{file_id}"):
            with st.spinner(get_text("ai_is_analyzing")):
                result = storage_manager.analyze_file_with_ai(file_id)
                if result.get("success"):
                    st.success(get_text("ai_analysis_completed"))
                    st.rerun()
                else:
                    st.error(get_text("ai_analysis_failed").format(result.get('error', get_text('unknown_error'))))
    else:
        # Display existing analysis results
        st.markdown(f"#### 📊 {get_text('analysis_results')}")
        col1, col2 = st.columns(2)
        with col1:
            st.metric(get_text("industry_category"), ai_analysis.get('industry_category', get_text('unclassified')))
            st.metric(get_text("confidence"), f"{ai_analysis.get('confidence_score', 0):.2%}")
        with col2:
            st.metric(get_text("analysis_method"), ai_analysis.get('method', get_text('unknown')))
            if ai_analysis.get('key_phrases'):
                st.markdown(f"**{get_text('key_phrases')}**")
                for phrase in ai_analysis['key_phrases'][:5]:
                    st.caption(f"• {phrase}")
        
        if ai_analysis.get('summary'):
            st.info(get_text("summary").format(ai_analysis['summary']))
    
    st.markdown("---")
    
    # AI Q&A area
    st.markdown(f"#### 💬 {get_text('ask_ai')}")
    
    # 输入框和麦克风按钮布局
    col_text, col_mic = st.columns([5, 1])
    
    with col_text:
        text_area_key = f"ai_question_{file_id}"
        
        # 直接使用text_area，它会自动从session_state读取值
        user_question = st.text_area(
            get_text("enter_your_question"),
            placeholder=get_text("question_placeholder"),
            height=100,
            key=text_area_key
        )
    
    with col_mic:
        st.markdown("<br>", unsafe_allow_html=True)  # 垂直对齐
        # 麦克风按钮
        mic_clicked = st.button("🎤", key=f"mic_button_{file_id}", help=get_text("voice_input"), use_container_width=True)
        
        # 检查是否有可用的语音识别方法
        available_methods = get_available_methods()
        if not available_methods:
            st.caption(f"⚠️ {get_text('speech_to_text')} {get_text('error')}")
    
    # 语音录制区域
    if mic_clicked or st.session_state.get(f"show_audio_recorder_{file_id}", False):
        st.session_state[f"show_audio_recorder_{file_id}"] = True
        
        st.markdown("---")
        st.markdown(f"**🎤 {get_text('voice_input')}**")
        
        # 使用Streamlit的音频输入组件
        audio_data = st.audio_input(
            get_text("click_to_record"),
            key=f"audio_input_{file_id}"
        )
        
        if audio_data is not None:
            # 显示音频播放器
            st.audio(audio_data, format="audio/wav")
            
            # 检查是否有可用的识别方法
            if len(available_methods) == 0:
                # 没有可用方法时显示提示
                st.warning("⚠️ No speech recognition methods available")
                if WHISPER_AVAILABLE and not check_ffmpeg():
                    st.info("💡 Please install ffmpeg to use Whisper, or install speech_recognition library")
                elif not WHISPER_AVAILABLE and not SPEECH_RECOGNITION_AVAILABLE:
                    st.info("💡 Please install speech recognition libraries: `pip install openai-whisper SpeechRecognition`")
            else:
                # 获取音频字节数据用于检测是否有新音频
                if hasattr(audio_data, 'read'):
                    audio_data.seek(0)
                    audio_bytes = audio_data.read()
                    audio_data.seek(0)  # 重置位置以便后续使用
                else:
                    audio_bytes = audio_data
                
                # 检查是否有新音频（通过比较音频数据的哈希值）
                audio_hash_key = f"audio_hash_{file_id}"
                current_audio_hash = hashlib.md5(audio_bytes).hexdigest()
                previous_audio_hash = st.session_state.get(audio_hash_key, None)
                
                # 如果有新音频且还没有识别过，自动触发识别
                if current_audio_hash != previous_audio_hash:
                    # 保存当前音频的哈希值
                    st.session_state[audio_hash_key] = current_audio_hash
                    
                    # 自动触发识别
                    with st.spinner(f"🎤 {get_text('auto_transcribing')}"):
                        try:
                            # 检查音频数据是否为空
                            if not audio_bytes or len(audio_bytes) == 0:
                                st.error(f"❌ {get_text('audio_data_empty')}")
                            else:
                                # 自动选择最佳方法进行识别（无需用户选择）
                                transcribed_text = transcribe_audio(audio_bytes)
                                
                                if transcribed_text and transcribed_text.strip():
                                    # 直接更新text_area的key对应的值（在rerun之前）
                                    text_area_key = f"ai_question_{file_id}"
                                    # 如果key不存在，直接设置；如果存在，需要先删除再设置
                                    if text_area_key in st.session_state:
                                        # 使用特殊方法更新：先清除，再设置
                                        del st.session_state[text_area_key]
                                    st.session_state[text_area_key] = transcribed_text
                                    
                                    st.success(f"✅ {get_text('transcription_successful').format(transcribed_text[:50])}")
                                    st.session_state[f"show_audio_recorder_{file_id}"] = False
                                    # 清除音频哈希，以便下次录音时可以重新识别
                                    if audio_hash_key in st.session_state:
                                        del st.session_state[audio_hash_key]
                                    st.rerun()
                                else:
                                    # 错误信息已经在transcribe_audio函数中显示，这里只显示通用提示
                                    st.warning(f"⚠️ {get_text('speech_recognition_failed')}")
                        except Exception as e:
                            st.error(f"❌ {get_text('error_processing_audio').format(str(e))}")
                else:
                    # 如果已经识别过当前音频，显示已识别的文本（如果有）
                    text_area_key = f"ai_question_{file_id}"
                    if text_area_key in st.session_state and st.session_state[text_area_key]:
                        st.info(f"📝 {get_text('transcribed').format(st.session_state[text_area_key][:100])}")
        
        # 关闭录音区域按钮
        if st.button(f"❌ {get_text('close')}", key=f"close_recorder_{file_id}"):
            st.session_state[f"show_audio_recorder_{file_id}"] = False
            st.rerun()
        
        st.markdown("---")
    
    col_ask, col_auto = st.columns([3, 1])
    with col_ask:
        if st.button(f"🚀 {get_text('ask')}", key=f"ask_ai_{file_id}", type="primary", use_container_width=True):
            if user_question:
                with st.spinner(f"🤔 {get_text('ai_is_thinking')}"):
                    result = storage_manager.generate_ai_report(file_id, user_question)
                    if result.get("success"):
                        st.session_state[f"ai_response_{file_id}"] = result.get("response", "")
                        st.rerun()
                    else:
                        st.error(get_text("ai_response_failed").format(result.get('error', get_text('unknown_error'))))
            else:
                st.warning(get_text("please_enter_question"))
    
    with col_auto:
        if st.button(f"📁 {get_text('auto_classify')}", key=f"auto_classify_{file_id}", use_container_width=True):
            if ai_analysis:
                category = ai_analysis.get('industry_category', 'Unclassified')
                confidence = ai_analysis.get('confidence_score', 0)
                
                # 调试信息
                print(f"[DEBUG] auto_classify: 原始分类: {category}, 置信度: {confidence}")
                
                # 统一转换为英文分类名称进行比较（数据库存储的是英文）
                eng_category = storage_manager._to_english_category(category) if category else 'Unclassified'
                print(f"[DEBUG] auto_classify: 转换后分类: {eng_category}")
                
                if eng_category and eng_category != 'Unclassified':
                    # 检查置信度（如果置信度太低，给出警告但仍然尝试分类）
                    if confidence and confidence < 0.2:
                        st.warning(f"⚠️ Low confidence ({confidence:.1%}), but attempting classification...")
                    
                    result = storage_manager.move_file_to_industry_folder(file_id, eng_category)
                    if result.get("success"):
                        folder_id = result.get("folder_id")
                        st.success(f"✅ {get_text('file_moved_to').format(eng_category)}")
                        # Automatically switch to the corresponding folder
                        if folder_id:
                            st.session_state.current_folder_id = folder_id
                            st.info(f"💡 {get_text('automatically_switched_to_folder').format(eng_category)}")
                        st.rerun()
                    else:
                        error_msg = result.get("error", get_text('unknown_error'))
                        st.error(f"❌ {get_text('classification_failed').format(error_msg)}")
                else:
                    # 提供更详细的错误信息
                    if category:
                        st.warning(f"⚠️ {get_text('unable_to_determine_classification')} (Category: {category}, Confidence: {confidence:.1%} if available)")
                    else:
                        st.warning(get_text("unable_to_determine_classification"))
            else:
                st.warning(get_text("please_perform_ai_analysis_first"))
    
    # Display AI response
    if st.session_state.get(f"ai_response_{file_id}"):
        st.markdown("---")
        st.markdown(f"#### 🤖 {get_text('ai_response')}")
        st.markdown(st.session_state[f"ai_response_{file_id}"])
    
    # 底部返回按钮（可选，顶部已有）
    st.markdown("---")
    if st.button(f"← {get_text('back_to_file_list')}", key=f"back_to_list_{file_id}", use_container_width=True, type="secondary"):
        st.session_state.viewing_file_id = None
        if f"ai_response_{file_id}" in st.session_state:
            del st.session_state[f"ai_response_{file_id}"]
        st.rerun()
