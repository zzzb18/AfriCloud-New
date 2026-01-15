# OCR配置说明

## ✅ 当前配置

**仅使用Tesseract OCR** - 轻量级OCR引擎，内存占用约50-100MB，避免内存溢出风险。

## 📦 安装步骤

### 1. 系统安装Tesseract OCR

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

### 2. Python依赖安装

```bash
pip install pytesseract Pillow
```

或使用requirements文件：
```bash
pip install -r requirements.txt
```

### 3. 验证安装

```bash
# 检查Tesseract版本
tesseract --version

# Python测试
python -c "import pytesseract; from PIL import Image; print('✅ Tesseract可用')"
```

## 🚀 使用方法

应用会自动检测并使用Tesseract OCR，无需任何配置！

启动应用：
```bash
streamlit run app.py
```

启动时会看到：
```
[DEBUG] ✅ Tesseract OCR可用（轻量级，内存占用约50-100MB，无需加载模型）
[DEBUG] ✅ OCR初始化 - 使用Tesseract OCR（轻量级，内存占用约50-100MB，无需加载模型）
```

## 🌐 语言支持

### 默认：仅英文
应用默认只识别英文，内存占用最小。

### 启用中文识别
如需中文识别，设置环境变量：
```bash
export ENABLE_CHINESE_OCR=true
streamlit run app.py
```

## 📊 内存占用

| OCR引擎 | 内存占用 | 状态 |
|--------|---------|------|
| **Tesseract** | **~50-100MB** | ✅ **当前使用** |
| ~~EasyOCR~~ | ~~~500-2GB~~ | ❌ **已移除** |

## ⚙️ 环境变量

| 变量 | 说明 | 默认值 |
|------|------|--------|
| `ENABLE_CHINESE_OCR` | 启用中文识别 | `false` |
| `DISABLE_OCR` | 禁用OCR | `false` |

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

### 问题3：pytesseract导入失败

**解决方案：**
```bash
pip install --upgrade pytesseract Pillow
```

## ✨ 优势

使用Tesseract OCR的优势：

1. ✅ **内存占用小**：只需50-100MB，不会导致内存溢出
2. ✅ **无需加载模型**：启动即用，无需等待模型加载
3. ✅ **速度快**：识别速度快
4. ✅ **稳定可靠**：成熟的开源项目，广泛使用
5. ✅ **多语言支持**：支持100+种语言
6. ✅ **免费开源**：完全免费，无使用限制

## 📝 注意事项

- **已完全移除EasyOCR**：避免内存溢出风险
- **仅使用Tesseract OCR**：轻量级，稳定可靠
- **无需模型加载**：Tesseract不需要加载大型模型文件

## 🔗 相关文档

- [详细安装说明](./INSTALL_TESSERACT.md)
- [快速开始指南](./QUICK_START_TESSERACT.md)
