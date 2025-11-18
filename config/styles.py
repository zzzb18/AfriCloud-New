"""CSS样式定义"""
CSS_STYLES = """
<style>
    /* 全局样式 - 云盘风格 */
    .main {
        background: #f5f7fa;
        color: #333;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', sans-serif;
    }
    
    /* 隐藏Streamlit默认元素 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    /* header {visibility: hidden;} */  /* 注释掉，保留header以便显示侧边栏切换按钮 */
    
    /* 顶部导航栏样式 */
    .top-navbar {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 12px 24px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        border-radius: 0 0 8px 8px;
    }
    
    .top-navbar h1 {
        color: white;
        margin: 0;
        font-size: 20px;
        font-weight: 600;
    }
    
    /* 标题样式 */
    h1, h2, h3, h4, h5, h6 {
        color: #1a1a1a;
        font-weight: 600;
        margin-bottom: 16px;
    }

    /* 按钮样式 - 云盘风格 */
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 10px 20px;
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 2px 4px rgba(102, 126, 234, 0.3);
        width: 100%;
    }

    .stButton>button:hover {
        background: linear-gradient(135deg, #5568d3 0%, #6a3d8f 100%);
        transform: translateY(-2px);
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* 次要按钮 */
    button[kind="secondary"] {
        background: #f0f0f0 !important;
        color: #333 !important;
        border: 1px solid #ddd !important;
    }
    
    button[kind="secondary"]:hover {
        background: #e0e0e0 !important;
    }
    
    /* 文件卡片样式 - 云盘风格 */
    .file-card {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 20px;
        margin-bottom: 16px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
        cursor: pointer;
    }

    .file-card:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
        border-color: #667eea;
    }
    
    /* 文件图标容器 */
    .file-icon-container {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 48px;
        height: 48px;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        border-radius: 8px;
        margin-right: 16px;
        font-size: 24px;
    }
    
    /* 统计卡片样式 */
    .metric-card {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 20px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        transition: all 0.3s ease;
    }
    
    .metric-card:hover {
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        transform: translateY(-2px);
    }
    
    /* 侧边栏样式 */
    [data-testid="stSidebar"] {
        background: white;
        border-right: 1px solid #e8e8e8;
    }
    
    /* 减少侧边栏组件间距 */
    [data-testid="stSidebar"] .element-container {
        margin-bottom: 8px !important;
    }
    
    [data-testid="stSidebar"] .stSelectbox {
        margin-bottom: 8px !important;
    }
    
    [data-testid="stSidebar"] .stButton {
        margin-bottom: 4px !important;
    }
    
    [data-testid="stSidebar"] hr {
        margin: 8px 0 !important;
    }
    
    /* 减少标题和副标题间距 */
    [data-testid="stSidebar"] h2 {
        margin-bottom: 4px !important;
    }
    
    [data-testid="stSidebar"] p {
        margin-bottom: 4px !important;
    }

    /* 工具栏样式 */
    .toolbar {
        background: white;
        padding: 16px;
        border-radius: 8px;
        margin-bottom: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
        display: flex;
        align-items: center;
        gap: 12px;
    }
    
    /* 搜索框样式 */
    .stTextInput>div>div>input {
        border-radius: 20px;
        border: 1px solid #e8e8e8;
        padding: 8px 16px;
    }
    
    .stTextInput>div>div>input:focus {
        border-color: #667eea;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
    }
    
    /* 文件夹样式 */
    .folder-item {
        padding: 12px 16px;
        border-radius: 6px;
        margin-bottom: 4px;
        cursor: pointer;
        transition: all 0.2s ease;
    }
    
    .folder-item:hover {
        background: #f5f7fa;
    }
    
    /* 状态标签 */
    .status-badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 12px;
        font-size: 12px;
        font-weight: 500;
    }
    
    .status-cached {
        background: #dcfce7;
        color: #166534;
    }
    
    .status-cloud {
        background: #dbeafe;
        color: #1e40af;
    }
    
    /* 预览区域 */
    .preview-section {
        background: white;
        border: 1px solid #e8e8e8;
        border-radius: 8px;
        padding: 24px;
        margin-top: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* 操作按钮组 */
    .action-buttons {
        display: flex;
        gap: 8px;
        flex-wrap: wrap;
    }
    
    /* 文件列表容器 */
    .files-container {
        background: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* 分隔线 */
    hr {
        border: none;
        border-top: 1px solid #e8e8e8;
        margin: 20px 0;
    }
    
    /* 输入框样式 */
    .stTextInput>div>div>input,
    .stNumberInput>div>div>input {
        border-radius: 6px;
        border: 1px solid #e8e8e8;
    }
    
    /* 选择框样式 */
    .stSelectbox>div>div {
        border-radius: 6px;
    }
    
    /* 展开器样式 */
    .streamlit-expanderHeader {
        font-weight: 600;
        color: #333;
    }
    
    /* 成功/错误消息样式 */
    .stSuccess {
        background: #dcfce7;
        border-left: 4px solid #10b981;
        border-radius: 6px;
    }
    
    .stError {
        background: #fee2e2;
        border-left: 4px solid #ef4444;
        border-radius: 6px;
    }
    
    .stWarning {
        background: #fef3c7;
        border-left: 4px solid #f59e0b;
        border-radius: 6px;
    }
    
    .stInfo {
        background: #dbeafe;
        border-left: 4px solid #3b82f6;
        border-radius: 6px;
    }
</style>
"""
