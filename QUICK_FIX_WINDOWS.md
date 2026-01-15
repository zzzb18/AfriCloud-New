# Windows快速修复指南

## 🚨 问题

看到错误信息：
```
⚠️ Tesseract未安装或不在PATH中: tesseract is not installed or it's not in your PATH
```

## ⚡ 快速解决方案

### 方法1：使用安装助手脚本（推荐）

1. **以管理员身份打开PowerShell**
   - 右键点击"开始"菜单
   - 选择"Windows PowerShell (管理员)"

2. **运行安装助手**
   ```powershell
   cd "C:\Users\alexhan\Downloads\AfriCloud-main\AfriCloud-main\Africloud"
   .\setup_tesseract_windows.ps1
   ```

3. **按照提示操作**

### 方法2：手动安装（3步）

#### 步骤1：下载安装Tesseract

1. 访问：https://github.com/UB-Mannheim/tesseract/wiki
2. 下载最新Windows安装包（例如：`tesseract-ocr-w64-setup-5.x.x.exe`）
3. 运行安装程序
4. **重要**：安装时选择"Chinese Simplified"语言包
5. 记住安装路径（默认：`C:\Program Files\Tesseract-OCR`）

#### 步骤2：添加到PATH

**方法A：通过图形界面**
1. 按 `Win + R`，输入 `sysdm.cpl`，回车
2. 点击"高级"选项卡 → "环境变量"
3. 在"系统变量"中找到`Path`，点击"编辑"
4. 点击"新建"，添加：`C:\Program Files\Tesseract-OCR`
5. 点击"确定"保存所有窗口

**方法B：通过PowerShell（管理员）**
```powershell
$tesseractPath = "C:\Program Files\Tesseract-OCR"
$currentPath = [Environment]::GetEnvironmentVariable("Path", "Machine")
[Environment]::SetEnvironmentVariable("Path", "$currentPath;$tesseractPath", "Machine")
```

#### 步骤3：安装Python依赖

```bash
pip install pytesseract Pillow
```

### 方法3：使用包管理器（如果已安装）

**Chocolatey:**
```powershell
choco install tesseract
```

**Scoop:**
```powershell
scoop install tesseract
```

## ✅ 验证安装

### 1. 检查Tesseract

打开**新的**命令提示符或PowerShell（重要：需要重新打开以加载新的PATH）：
```bash
tesseract --version
```

应该显示版本号，例如：
```
tesseract 5.3.3
```

### 2. 检查Python库

```bash
python -c "import pytesseract; print('✅ OK')"
```

### 3. 检查语言包

```bash
tesseract --list-langs
```

应该看到：
```
chi_sim
eng
```

## 🔧 如果仍然找不到

### 临时解决方案：在代码中指定路径

如果PATH配置有问题，可以临时在代码中指定路径。

编辑 `utils/dependencies.py`，在文件开头添加：

```python
import os
import platform

# Windows: 手动指定Tesseract路径（如果不在PATH中）
if platform.system() == "Windows":
    tesseract_path = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
    if os.path.exists(tesseract_path):
        import pytesseract
        pytesseract.pytesseract.tesseract_cmd = tesseract_path
```

## 🎯 完成

安装完成后，重启应用：
```bash
streamlit run app.py
```

应该看到：
```
[DEBUG] ✅ Tesseract OCR可用（轻量级，内存占用约50-100MB）
```

## 📚 更多帮助

- [详细安装说明](./INSTALL_TESSERACT_WINDOWS.md)
- [完整OCR文档](./README_OCR.md)
