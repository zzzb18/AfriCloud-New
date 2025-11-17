# 🌾 Agribusiness Expert AI Cloud

智能农业文件管理和分析平台

## 📁 项目结构

```
AfriCloud/
├── app.py                      # 主应用入口
├── app_4.py                    # 原始单文件（已重构）
├── requirements.txt            # 依赖包列表
├── config/                     # 配置模块
│   ├── __init__.py
│   ├── settings.py             # 应用配置
│   └── styles.py              # CSS样式
├── core/                       # 核心业务逻辑
│   ├── __init__.py
│   └── storage_manager.py     # 云存储管理器
├── components/                 # UI组件（待扩展）
│   └── __init__.py
└── utils/                      # 工具函数
    ├── __init__.py
    └── dependencies.py        # 依赖检查
```

## 🚀 快速开始

### 1. 创建并激活虚拟环境

**Windows (PowerShell):**
```powershell
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\Activate.ps1
```

**Windows (CMD):**
```cmd
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
venv\Scripts\activate.bat
```

**Linux/Mac:**
```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate
```

### 2. 安装依赖

**安装核心依赖（推荐，快速启动）:**
```bash
pip install -r requirements-base.txt
```

**或安装所有依赖（包括可选功能）:**
```bash
pip install -r requirements.txt
```

### 3. 运行应用

**在虚拟环境中运行:**
```bash
python -m streamlit run app.py
```

**或使用便捷脚本（Windows）:**
```bash
.\run.bat
```

**或使用便捷脚本（Linux/Mac）:**
```bash
chmod +x run.sh
./run.sh
```

### 4. 访问应用

浏览器会自动打开 `http://localhost:8501`

### 5. 退出虚拟环境

```bash
deactivate
```

## 📦 依赖说明

### 核心依赖（requirements-base.txt）
- `streamlit` - Web框架
- `pandas` - 数据处理
- `numpy` - 数值计算
- `jieba` - 中文分词
- `matplotlib` - 数据可视化
- `seaborn` - 统计图表
- `openpyxl`, `xlrd` - Excel文件支持

### 可选依赖（requirements.txt中的额外包）
- `PyMuPDF` - PDF预览支持
- `easyocr` - OCR文字识别
- `scikit-learn` - 机器学习分类
- `transformers`, `torch` - 深度学习模型
- `openai` - OpenAI API集成
- `python-docx` - Word文档支持

> 💡 **提示**: 如果只需要基本功能，安装 `requirements-base.txt` 即可。可选依赖用于增强功能（AI分析、OCR等）。

## 🔧 配置

### DeepSeek API配置

在 `.streamlit/secrets.toml` 中配置（如果使用Streamlit Cloud）：

```toml
DEEPSEEK_API_KEY = "your-api-key-here"
```

或在环境变量中设置：

```bash
export DEEPSEEK_API_KEY="your-api-key-here"
```

## 📝 功能特性

- ✅ 文件上传和管理
- ✅ 文件夹组织
- ✅ 在线文件预览（图片、PDF、Excel等）
- ✅ AI智能分析
- ✅ 行业分类
- ✅ 智能报告生成
- ✅ 天气和遥感数据
- ✅ 农业计算器

## 🛠️ 开发

项目已从单文件重构为模块化结构，便于维护和扩展。

### 模块说明

- **config/** - 配置和样式
- **core/** - 核心业务逻辑
- **components/** - UI组件（可进一步拆分）
- **utils/** - 工具函数

## 📄 许可证

MIT License

"# AfriCloud-New" 
