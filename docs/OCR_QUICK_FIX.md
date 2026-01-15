# OCR内存溢出快速修复指南

## 问题症状

- 服务启动时崩溃
- OCR模型加载时出现 `MemoryError`
- 进程被系统杀死（OOM Killer）

## 快速解决方案

### 方案1：禁用OCR（最快，如果不需要OCR功能）

```bash
export DISABLE_OCR=1
streamlit run app.py
```

### 方案2：使用Tesseract OCR（推荐，轻量级）

**步骤1：安装Tesseract**

```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim

# macOS
brew install tesseract

# 验证安装
tesseract --version
```

**步骤2：安装Python库**

```bash
pip install pytesseract pillow
```

**步骤3：配置使用Tesseract**

```bash
export OCR_ENGINE=tesseract
export DISABLE_EASYOCR=1
streamlit run app.py
```

### 方案3：只加载英文EasyOCR（减少内存）

```bash
# 默认只加载英文模型（已实现）
# 如果需要中文，设置：
export ENABLE_CHINESE_OCR=true

streamlit run app.py
```

### 方案4：使用PaddleOCR（中等内存占用）

```bash
pip install paddlepaddle paddleocr

export OCR_ENGINE=paddleocr
export DISABLE_EASYOCR=1
streamlit run app.py
```

## 内存优化技巧

### 1. 设置内存限制

```bash
# Linux: 限制进程内存为2GB
ulimit -v 2097152
streamlit run app.py
```

### 2. 监控内存使用

```bash
# 安装psutil
pip install psutil

# 代码会自动监控内存
```

### 3. 自动卸载模型

代码已实现自动卸载功能，使用完后会自动释放内存。

## 检查当前配置

在应用启动时，查看日志输出：

```
[DEBUG] OCR初始化 - OCR_AVAILABLE: True
[DEBUG] 使用Tesseract OCR引擎  # 或 EasyOCR/PaddleOCR
```

## 推荐配置（根据服务器内存）

| 服务器内存 | 推荐方案 | 环境变量设置 |
|-----------|---------|------------|
| < 1GB | 禁用OCR或使用API | `DISABLE_OCR=1` |
| 1-2GB | Tesseract OCR | `OCR_ENGINE=tesseract` |
| 2-4GB | PaddleOCR或EasyOCR英文 | `OCR_ENGINE=paddleocr` 或默认 |
| > 4GB | EasyOCR完整版 | `ENABLE_CHINESE_OCR=true` |

## 故障排除

### 问题：Tesseract找不到

**解决方案：**
```bash
# 检查Tesseract路径
which tesseract

# 如果找不到，设置环境变量
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata
```

### 问题：仍然内存溢出

**解决方案：**
1. 检查其他进程占用内存：`free -h`
2. 减少并发请求
3. 使用更轻量的OCR方案
4. 考虑升级服务器内存

### 问题：OCR准确度下降

**解决方案：**
1. 使用图片预处理（去噪、增强对比度）
2. 调整OCR参数
3. 考虑使用外部API服务（Google Vision API等）

## 测试OCR功能

启动应用后，上传一张包含文字的图片，查看是否能正常识别。

如果看到错误信息，检查日志输出中的 `[DEBUG]` 信息。
