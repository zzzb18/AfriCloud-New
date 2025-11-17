# 环境配置指南

## 📋 快速配置（Windows）

### 方法1：使用自动配置脚本（推荐）

```powershell
# 运行自动配置脚本
.\setup_env.bat
```

脚本会自动：
1. 创建虚拟环境
2. 激活虚拟环境
3. 升级pip
4. 安装核心依赖

### 方法2：手动配置

```powershell
# 1. 创建虚拟环境
python -m venv venv

# 2. 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 3. 升级pip
python -m pip install --upgrade pip

# 4. 安装核心依赖
pip install -r requirements-base.txt

# 5. （可选）安装所有依赖（包括AI功能）
pip install -r requirements.txt
```

## 🚀 运行应用

### 方法1：使用运行脚本

```powershell
.\run.bat
```

### 方法2：手动运行

```powershell
# 确保虚拟环境已激活
.\venv\Scripts\Activate.ps1

# 运行应用
python -m streamlit run app.py
```

## 📦 依赖说明

### requirements-base.txt（核心依赖）
包含运行应用所需的最小依赖集：
- Streamlit框架
- 数据处理（pandas, numpy）
- 中文分词（jieba）
- 数据可视化（matplotlib, seaborn）
- Excel支持（openpyxl, xlrd）

### requirements.txt（完整依赖）
包含所有可选功能：
- PDF预览（PyMuPDF）
- OCR识别（easyocr）
- 机器学习（scikit-learn）
- 深度学习（transformers, torch）
- OpenAI集成（openai）

## ⚠️ 常见问题

### 1. PowerShell执行策略限制

如果遇到"无法加载脚本"错误，运行：
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### 2. 虚拟环境未激活

确保命令提示符前有 `(venv)` 标识。

### 3. 端口被占用

如果8501端口被占用，使用：
```bash
python -m streamlit run app.py --server.port 8502
```

## 🔄 更新依赖

```powershell
# 激活虚拟环境
.\venv\Scripts\Activate.ps1

# 更新所有包
pip install --upgrade -r requirements-base.txt
```

## 🗑️ 删除虚拟环境

```powershell
# 退出虚拟环境
deactivate

# 删除venv文件夹
Remove-Item -Recurse -Force venv
```

