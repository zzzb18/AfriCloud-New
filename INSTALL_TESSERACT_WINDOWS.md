# Windows系统安装Tesseract OCR指南

## 📥 下载安装

### 方法1：使用安装包（推荐）

1. **下载安装包**
   - 访问：https://github.com/UB-Mannheim/tesseract/wiki
   - 下载最新版本的Windows安装包（例如：`tesseract-ocr-w64-setup-5.x.x.exe`）

2. **安装步骤**
   - 运行下载的安装程序
   - **重要**：安装时选择安装中文语言包（Chinese Simplified）
   - 记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

3. **添加到系统PATH**
   - 打开"系统属性" → "环境变量"
   - 在"系统变量"中找到`Path`，点击"编辑"
   - 添加Tesseract安装路径：`C:\Program Files\Tesseract-OCR`
   - 点击"确定"保存

4. **验证安装**
   - 打开命令提示符（CMD）或PowerShell
   - 运行：`tesseract --version`
   - 如果显示版本号，说明安装成功

### 方法2：使用Chocolatey（如果已安装）

```powershell
choco install tesseract
```

### 方法3：使用Scoop（如果已安装）

```powershell
scoop install tesseract
```

## 🔧 配置Python环境

### 1. 安装Python依赖

```bash
pip install pytesseract Pillow
```

### 2. 配置Tesseract路径（如果需要）

如果Tesseract不在PATH中，可以在代码中指定路径：

```python
import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
```

## ✅ 验证安装

### 测试1：命令行测试

```bash
tesseract --version
```

应该显示类似：
```
tesseract 5.x.x
```

### 测试2：Python测试

```python
import pytesseract
from PIL import Image

# 测试
print(pytesseract.get_tesseract_version())
```

### 测试3：检查语言包

```bash
tesseract --list-langs
```

应该看到：
```
chi_sim
eng
```

## 🚨 常见问题

### 问题1：找不到tesseract命令

**解决方案：**
1. 检查是否添加到PATH
2. 重启命令提示符/PowerShell
3. 如果仍不行，手动指定路径（见上方配置）

### 问题2：中文识别失败

**解决方案：**
1. 确保安装了中文语言包
2. 检查语言包是否存在：
   ```bash
   dir "C:\Program Files\Tesseract-OCR\tessdata"
   ```
3. 应该看到 `chi_sim.traineddata` 文件

### 问题3：Python找不到tesseract

**解决方案：**

在代码中添加路径配置（临时方案）：
```python
import pytesseract
import os

# 设置Tesseract路径
tesseract_path = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
if os.path.exists(tesseract_path):
    pytesseract.pytesseract.tesseract_cmd = tesseract_path
```

或者在环境变量中设置：
```powershell
$env:TESSDATA_PREFIX = "C:\Program Files\Tesseract-OCR\tessdata"
```

## 📝 快速安装脚本（PowerShell）

```powershell
# 下载并安装Tesseract（需要管理员权限）
# 注意：需要手动下载安装包，此脚本仅作参考

# 1. 下载安装包
$url = "https://digi.bib.uni-mannheim.de/tesseract/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
$output = "$env:TEMP\tesseract-installer.exe"
Invoke-WebRequest -Uri $url -OutFile $output

# 2. 运行安装程序（需要手动操作）
Start-Process $output -Wait

# 3. 添加到PATH（需要管理员权限）
$tesseractPath = "C:\Program Files\Tesseract-OCR"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
if ($currentPath -notlike "*$tesseractPath*") {
    [Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")
}

# 4. 安装Python依赖
pip install pytesseract Pillow
```

## 🎯 安装后测试

启动应用：
```bash
streamlit run app.py
```

应该看到：
```
[DEBUG] ✅ Tesseract OCR可用（轻量级，内存占用约50-100MB，无需加载模型）
```

## 📚 更多信息

- Tesseract官方文档：https://tesseract-ocr.github.io/
- Windows安装包：https://github.com/UB-Mannheim/tesseract/wiki
- Python pytesseract文档：https://pypi.org/project/pytesseract/
