"""File preview component"""
import streamlit as st
import pandas as pd
import io
from core.storage_manager import CloudStorageManager
from utils.dependencies import PDF_AVAILABLE


def render_file_preview_modal(storage_manager: CloudStorageManager, file_id: int):
    """Render file preview modal"""
    # Get file info directly by file_id (not dependent on folder)
    print(f"[DEBUG] file_preview: Attempting to preview file - ID: {file_id}")
    file = storage_manager.get_file_by_id(file_id)
    
    if not file:
        print(f"[DEBUG] file_preview: File not found - ID: {file_id}")
        st.error(f"File not found (ID: {file_id})")
        return
    
    print(f"[DEBUG] file_preview: File found - Name: {file.get('filename')}, Path: {file.get('file_path')}")
    
    # Preview modal styles
    st.markdown("""
    <style>
    .preview-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.5);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Preview area
    st.markdown("---")
    st.markdown(f"#### 📄 {file.get('filename', 'Unknown')}")
    
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
    user_question = st.text_area(
        "Enter your question",
        placeholder="e.g., What is the main content of this file? What trends are in the data?",
        height=100,
        key=f"ai_question_{file_id}"
    )
    
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
    
    # Close button
    st.markdown("---")
    if st.button("❌ Close Preview", key=f"close_preview_{file_id}", use_container_width=True):
        st.session_state[f"preview_file_{file_id}"] = False
        if f"ai_response_{file_id}" in st.session_state:
            del st.session_state[f"ai_response_{file_id}"]
        st.rerun()
