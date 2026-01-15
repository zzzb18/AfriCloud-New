# OCR内存溢出问题 - 快速解决方案

## 🚨 问题描述

服务器在加载OCR模型时内存溢出，导致服务崩溃。

## ⚡ 快速解决方案（3选1）

### 方案1：禁用OCR（最快，如果不需要OCR功能）

**Windows:**
```cmd
set DISABLE_OCR=1
streamlit run app.py
```

**Linux/Mac:**
```bash
export DISABLE_OCR=1
streamlit run app.py
```

### 方案2：只使用英文EasyOCR（减少内存占用，已默认）

代码已默认只加载英文模型，如果需要中文：

```bash
export ENABLE_CHINESE_OCR=true
```

### 方案3：使用Tesseract OCR（推荐，最轻量）

**安装Tesseract:**

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim
pip install pytesseract pillow
```

**macOS:**
```bash
brew install tesseract
pip install pytesseract pillow
```

**Windows:**
1. 下载安装：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装Python库：`pip install pytesseract pillow`

**配置使用:**
```bash
export OCR_ENGINE=tesseract
export DISABLE_EASYOCR=1
streamlit run app.py
```

## 📊 内存占用对比

| OCR引擎 | 内存占用 | 准确度 | 速度 |
|--------|---------|--------|------|
| Tesseract | ~50-100MB | ⭐⭐⭐ | ⭐⭐⭐⭐ |
| PaddleOCR | ~200-300MB | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| EasyOCR (英文) | ~500-800MB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| EasyOCR (中英文) | ~1-2GB | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

## 🔧 详细文档

- [完整优化方案](./docs/OCR_MEMORY_OPTIMIZATION.md)
- [快速修复指南](./docs/OCR_QUICK_FIX.md)

## 💡 推荐配置

根据服务器内存选择：

- **< 1GB**: 禁用OCR或使用外部API
- **1-2GB**: Tesseract OCR
- **2-4GB**: PaddleOCR 或 EasyOCR英文
- **> 4GB**: EasyOCR完整版

## 🛠️ 使用修复脚本

**Linux/Mac:**
```bash
chmod +x fix_ocr_memory.sh
./fix_ocr_memory.sh
```

**Windows:**
```cmd
fix_ocr_memory.bat
```

## ❓ 故障排除

### 问题：仍然内存溢出

1. 检查其他进程占用内存
2. 减少并发请求
3. 使用更轻量的OCR方案
4. 考虑升级服务器内存

### 问题：OCR准确度下降

1. 使用图片预处理
2. 调整OCR参数
3. 考虑使用外部API服务

## 📝 注意事项

- 修改环境变量后需要重启应用
- Windows使用 `setx` 设置永久环境变量
- Linux/Mac使用 `export` 设置当前会话，或添加到 `~/.bashrc` 永久生效
