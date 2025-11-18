# Whisper模型加载优化指南

## 为什么Streamlit Cloud加载更快？

### 主要原因：

1. **模型缓存**
   - Streamlit Cloud可能已经缓存了模型文件（在 `~/.cache/whisper/` 目录）
   - 您的服务器如果是第一次使用，需要从网络下载模型文件（约75MB for tiny模型）
   - 下载速度取决于网络连接质量

2. **网络速度**
   - Streamlit Cloud通常有更好的网络连接到Hugging Face/GitHub
   - 您的服务器可能网络较慢，特别是如果在中国大陆，访问Hugging Face可能较慢

3. **磁盘I/O性能**
   - Streamlit Cloud使用高性能SSD
   - 您的服务器可能使用较慢的存储设备

4. **CPU性能**
   - 模型加载需要解压和加载到内存，CPU性能影响加载速度

## 优化方案

### 方案1：预下载模型（推荐）

在服务器上手动预下载模型，避免首次使用时下载：

```bash
# 激活conda环境
conda activate africloud

# 进入Python环境
python -c "import whisper; whisper.load_model('tiny')"
```

这会自动下载模型到 `~/.cache/whisper/tiny.pt`，之后加载会快很多。

### 方案2：使用国内镜像（如果在中国）

如果您的服务器在中国，可以设置Hugging Face镜像：

```bash
export HF_ENDPOINT=https://hf-mirror.com
```

或者在代码中设置：

```python
import os
os.environ['HF_ENDPOINT'] = 'https://hf-mirror.com'
```

### 方案3：使用本地模型文件

如果您已经下载了模型文件，可以指定路径：

```python
model = whisper.load_model("tiny", download_root="/path/to/models")
```

### 方案4：延迟加载（已实现）

模型现在只在需要时才加载，而不是启动时加载，这样可以：
- 避免启动时阻塞
- 只在用户实际使用语音功能时才加载

### 方案5：检查网络和存储性能

```bash
# 检查网络速度（下载Hugging Face）
curl -I https://huggingface.co

# 检查磁盘I/O
dd if=/dev/zero of=testfile bs=1M count=1000 conv=fdatasync
rm testfile

# 检查CPU性能
python -c "import time; start=time.time(); [i**2 for i in range(1000000)]; print(f'CPU test: {time.time()-start:.2f}s')"
```

## 模型大小对比

| 模型 | 参数量 | 文件大小 | 内存占用 | 速度 | 准确度 |
|------|--------|----------|----------|------|--------|
| tiny | 39M    | ~75MB    | ~1GB     | 最快 | 较低   |
| base | 74M    | ~142MB   | ~1GB     | 快   | 中等   |
| small| 244M   | ~466MB   | ~2GB     | 中等 | 较高   |

当前使用 `tiny` 模型，是内存占用最小的选择。

## 诊断命令

检查模型是否已缓存：

```bash
ls -lh ~/.cache/whisper/
```

如果看到 `tiny.pt` 文件，说明模型已下载，后续加载会快很多。

## 预期加载时间

- **首次下载+加载**：1-5分钟（取决于网络）
- **已缓存后加载**：5-30秒（取决于CPU和磁盘I/O）
- **Streamlit Cloud**：通常已缓存，5-15秒

