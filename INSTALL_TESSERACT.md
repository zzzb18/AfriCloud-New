# 安装Tesseract OCR（轻量级OCR方案）

## 系统安装Tesseract

### Ubuntu/Debian
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim
```

### macOS
```bash
brew install tesseract
```

### Windows
1. 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时选择安装中文语言包
3. 将Tesseract添加到系统PATH

## Python依赖安装

```bash
pip install -r requirements_ocr_tesseract.txt
```

或手动安装：
```bash
pip install pytesseract Pillow
```

## 验证安装

```bash
# 检查Tesseract版本
tesseract --version

# Python测试
python -c "import pytesseract; from PIL import Image; print('✅ Tesseract可用')"
```

## 配置使用

应用会自动检测并使用Tesseract（如果已安装）。

如果需要强制使用Tesseract：
```bash
export OCR_ENGINE=tesseract
```

如果需要中文识别：
```bash
export ENABLE_CHINESE_OCR=true
```

## 启动应用

```bash
streamlit run app.py
```

应用启动时会显示：
```
[DEBUG] ✅ Tesseract OCR可用（轻量级，推荐）
[DEBUG] OCR初始化 - 使用Tesseract OCR（轻量级，推荐）
```

## 故障排除

### 问题：找不到tesseract命令

**解决方案：**
```bash
# 检查安装位置
which tesseract

# 如果找不到，设置环境变量（Linux）
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Windows: 确保Tesseract在PATH中
```

### 问题：中文识别失败

**解决方案：**
```bash
# 确保安装了中文语言包
# Ubuntu/Debian
sudo apt-get install tesseract-ocr-chi-sim

# 验证语言包
tesseract --list-langs
```
