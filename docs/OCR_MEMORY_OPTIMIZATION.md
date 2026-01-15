# OCR内存优化解决方案

当服务器内存不足导致EasyOCR模型加载失败时，可以使用以下解决方案：

## 方案1：使用轻量级OCR替代方案（推荐）

### 1.1 Tesseract OCR（最轻量）

**优点：**
- ✅ 内存占用小（约50-100MB）
- ✅ 速度快
- ✅ 支持多语言
- ✅ 免费开源

**缺点：**
- ❌ 准确度略低于EasyOCR
- ❌ 需要系统安装Tesseract

**安装：**
```bash
# Ubuntu/Debian
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng

# macOS
brew install tesseract

# Windows
# 下载安装包：https://github.com/UB-Mannheim/tesseract/wiki
```

**Python依赖：**
```bash
pip install pytesseract pillow
```

### 1.2 PaddleOCR（轻量版）

**优点：**
- ✅ 内存占用中等（约200-300MB）
- ✅ 准确度高
- ✅ 支持中英文
- ✅ 可以只加载检测或识别模型

**缺点：**
- ❌ 比Tesseract占用更多内存
- ❌ 首次使用需要下载模型

**安装：**
```bash
pip install paddlepaddle paddleocr
```

## 方案2：优化EasyOCR使用

### 2.1 只加载英文模型（已实现）

```bash
# 默认只加载英文模型（更轻量）
# 如果需要中文，设置环境变量
export ENABLE_CHINESE_OCR=true
```

### 2.2 使用量化模型

EasyOCR支持量化模型，可以减少内存占用：
- 使用 `quantize=True` 参数（如果支持）
- 或使用预训练的量化版本

### 2.3 按需加载和卸载

代码已实现延迟加载，可以进一步优化：

```python
# 使用完后立即卸载模型
def unload_ocr_model(self):
    """卸载OCR模型释放内存"""
    if self.ocr_reader is not None:
        del self.ocr_reader
        self.ocr_reader = None
        import gc
        gc.collect()
        print("[DEBUG] OCR模型已卸载，内存已释放")
```

## 方案3：使用外部OCR API服务

### 3.1 Google Cloud Vision API

**优点：**
- ✅ 不占用本地内存
- ✅ 准确度高
- ✅ 支持多语言

**缺点：**
- ❌ 需要API密钥
- ❌ 有费用（但有免费额度）
- ❌ 需要网络连接

### 3.2 Azure Computer Vision

**优点：**
- ✅ 不占用本地内存
- ✅ 企业级服务
- ✅ 准确度高

**缺点：**
- ❌ 需要Azure账号
- ❌ 有费用

### 3.3 百度OCR API

**优点：**
- ✅ 中文识别准确度高
- ✅ 有免费额度
- ✅ 国内访问速度快

**缺点：**
- ❌ 需要API密钥
- ❌ 有费用限制

## 方案4：图片预处理优化

### 4.1 图片压缩和缩放

在OCR前压缩图片可以减少内存占用：

```python
from PIL import Image
import io

def compress_image_for_ocr(image_path, max_size=(1920, 1920), quality=85):
    """压缩图片用于OCR，减少内存占用"""
    img = Image.open(image_path)
    
    # 如果图片太大，先缩放
    if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
    
    # 转换为RGB（如果需要）
    if img.mode != 'RGB':
        img = img.convert('RGB')
    
    # 保存到内存
    buffer = io.BytesIO()
    img.save(buffer, format='JPEG', quality=quality, optimize=True)
    buffer.seek(0)
    
    return buffer
```

### 4.2 分批处理

对于多页PDF，逐页处理而不是一次性加载所有页面：

```python
# 已实现：逐页OCR，避免一次性加载所有页面到内存
```

## 方案5：内存限制和监控

### 5.1 设置内存限制

使用环境变量限制Python进程内存：

```bash
# 使用ulimit限制内存（Linux）
ulimit -v 2097152  # 限制2GB虚拟内存

# 或使用systemd限制（如果使用systemd）
```

### 5.2 内存监控

添加内存监控，在内存不足时自动卸载模型：

```python
import psutil
import os

def get_memory_usage():
    """获取当前进程内存使用量（MB）"""
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / 1024 / 1024

def check_memory_before_ocr(max_memory_mb=1500):
    """检查内存是否足够进行OCR"""
    current_memory = get_memory_usage()
    if current_memory > max_memory_mb:
        print(f"[DEBUG] 内存使用过高 ({current_memory:.1f}MB)，建议先释放内存")
        return False
    return True
```

## 推荐配置（根据服务器内存）

### 内存 < 1GB
```bash
# 禁用OCR，使用外部API
export DISABLE_OCR=1
# 或使用Tesseract OCR
```

### 内存 1-2GB
```bash
# 使用Tesseract OCR或只加载英文EasyOCR
export ENABLE_CHINESE_OCR=false
# 或使用PaddleOCR轻量版
```

### 内存 2-4GB
```bash
# 可以使用EasyOCR（只加载英文）
export ENABLE_CHINESE_OCR=false
# 或使用PaddleOCR完整版
```

### 内存 > 4GB
```bash
# 可以使用完整EasyOCR（中英文）
export ENABLE_CHINESE_OCR=true
```

## 快速切换方案

### 切换到Tesseract OCR

1. 安装Tesseract：
```bash
sudo apt-get install tesseract-ocr tesseract-ocr-chi-sim tesseract-ocr-eng
pip install pytesseract
```

2. 设置环境变量：
```bash
export USE_TESSERACT_OCR=1
export DISABLE_EASYOCR=1
```

### 切换到PaddleOCR

1. 安装PaddleOCR：
```bash
pip install paddlepaddle paddleocr
```

2. 设置环境变量：
```bash
export USE_PADDLE_OCR=1
export DISABLE_EASYOCR=1
```

### 禁用OCR

```bash
export DISABLE_OCR=1
```

## 故障排除

### 问题1：仍然内存溢出

**解决方案：**
1. 检查是否有其他进程占用内存
2. 减少并发请求
3. 使用更轻量的OCR方案
4. 增加服务器内存

### 问题2：OCR准确度下降

**解决方案：**
1. 使用图片预处理（去噪、增强对比度）
2. 调整OCR参数
3. 考虑使用外部API服务

### 问题3：OCR速度慢

**解决方案：**
1. 使用GPU加速（如果有GPU）
2. 图片预处理减少尺寸
3. 使用更快的OCR引擎（Tesseract）

## 总结

**对于内存不足的服务器，推荐优先级：**

1. **首选**：Tesseract OCR（最轻量，约50-100MB）
2. **次选**：PaddleOCR轻量版（约200-300MB）
3. **备选**：外部OCR API服务（不占内存）
4. **最后**：EasyOCR只加载英文模型（约500-800MB）
