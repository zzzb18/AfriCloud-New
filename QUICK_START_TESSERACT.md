# Tesseract OCR 快速开始指南

## ✅ 已完成集成

代码已更新，现在**默认优先使用Tesseract OCR**（轻量级，内存占用约50-100MB）。

## 🚀 快速安装

### 1. 安装Tesseract OCR（系统级）

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim
```

**macOS:**
```bash
brew install tesseract
```

**Windows:**
1. 下载安装：https://github.com/UB-Mannheim/tesseract/wiki
2. 安装时选择中文语言包
3. 确保添加到系统PATH

### 2. 安装Python依赖

```bash
pip install pytesseract Pillow
```

或使用requirements文件：
```bash
pip install -r requirements_ocr_tesseract.txt
```

### 3. 验证安装

```bash
# 检查Tesseract版本
tesseract --version

# Python测试
python -c "import pytesseract; from PIL import Image; print('✅ Tesseract可用')"
```

## 🎯 使用方法

### 默认使用（自动检测）

应用会自动检测并使用Tesseract（如果已安装）。无需任何配置！

启动应用：
```bash
streamlit run app.py
```

启动时会看到：
```
[DEBUG] ✅ Tesseract OCR可用（轻量级，推荐）
[DEBUG] OCR初始化 - 自动选择Tesseract OCR（轻量级，推荐）
```

### 强制使用Tesseract

如果需要强制使用Tesseract（即使EasyOCR已安装）：
```bash
export OCR_ENGINE=tesseract
streamlit run app.py
```

### 启用中文识别

默认只识别英文，如需中文：
```bash
export ENABLE_CHINESE_OCR=true
streamlit run app.py
```

### 回退到EasyOCR

如果Tesseract不可用，会自动回退到EasyOCR：
```bash
export OCR_ENGINE=easyocr
streamlit run app.py
```

## 📊 内存占用对比

| OCR引擎 | 内存占用 | 状态 |
|--------|---------|------|
| **Tesseract** | **~50-100MB** | ✅ **默认（推荐）** |
| EasyOCR英文 | ~500-800MB | 备用 |
| EasyOCR中英文 | ~1-2GB | 备用 |

## 🔍 功能对比

| 功能 | Tesseract | EasyOCR |
|------|-----------|---------|
| 内存占用 | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| 识别速度 | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| 准确度 | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ |
| 中文支持 | ✅ | ✅ |
| 安装难度 | ⭐⭐⭐ | ⭐⭐⭐⭐ |

## ❓ 故障排除

### 问题1：找不到tesseract命令

**解决方案：**
```bash
# Linux: 检查安装位置
which tesseract

# 如果找不到，设置环境变量
export TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata

# Windows: 确保Tesseract在PATH中
```

### 问题2：中文识别失败

**解决方案：**
```bash
# 确保安装了中文语言包
sudo apt-get install tesseract-ocr-chi-sim

# 验证语言包
tesseract --list-langs

# 应该看到: chi_sim, eng 等
```

### 问题3：仍然使用EasyOCR

**检查：**
1. 查看启动日志，确认使用的引擎
2. 如果Tesseract未安装，会自动回退到EasyOCR
3. 可以强制使用：`export OCR_ENGINE=tesseract`

## 📝 环境变量说明

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `OCR_ENGINE` | OCR引擎选择 | `tesseract`（如果可用） |
| `ENABLE_CHINESE_OCR` | 启用中文识别 | `false` |
| `DISABLE_OCR` | 禁用OCR | `false` |

## ✨ 优势

使用Tesseract OCR的优势：

1. ✅ **内存占用小**：只需50-100MB，不会导致内存溢出
2. ✅ **速度快**：识别速度快，无需加载大型模型
3. ✅ **稳定可靠**：成熟的开源项目，广泛使用
4. ✅ **多语言支持**：支持100+种语言
5. ✅ **免费开源**：完全免费，无使用限制

## 🎉 完成！

现在您的应用已经配置为使用轻量级的Tesseract OCR，不会再出现内存溢出问题！

如有问题，请查看：
- [详细安装说明](./INSTALL_TESSERACT.md)
- [OCR优化文档](./docs/OCR_MEMORY_OPTIMIZATION.md)
