# 语音识别替代方案（内存不足时）

当服务器内存不足无法运行Whisper模型时，可以使用以下替代方案：

## 方案1：使用 speech_recognition（推荐，不占用内存）

### 优点
- ✅ **不占用内存**：不需要加载模型到内存
- ✅ **免费**：使用Google Speech Recognition API（免费）
- ✅ **准确度高**：Google的识别准确度很高
- ✅ **即开即用**：无需下载模型文件

### 缺点
- ❌ **需要网络**：必须能够访问Google服务
- ❌ **依赖网络速度**：识别速度取决于网络

### 使用方法

#### 方法1：自动切换（推荐）
代码已自动实现：如果Whisper被禁用或加载失败，会自动使用speech_recognition。

#### 方法2：手动禁用Whisper
设置环境变量：
```bash
export DISABLE_WHISPER=1
```

或者在启动脚本中：
```bash
DISABLE_WHISPER=1 streamlit run app.py
```

### 依赖安装
确保已安装：
```bash
pip install SpeechRecognition
```

## 方案2：使用外部API服务

### 选项A：OpenAI Whisper API（付费）
- 优点：准确度高，无需本地资源
- 缺点：需要API密钥，有费用
- 使用：需要修改代码调用OpenAI API

### 选项B：Azure Speech Services（付费）
- 优点：企业级服务，准确度高
- 缺点：需要Azure账号和API密钥
- 使用：需要修改代码集成Azure SDK

### 选项C：Google Cloud Speech-to-Text（付费）
- 优点：准确度高，支持多语言
- 缺点：需要Google Cloud账号和API密钥
- 使用：需要修改代码集成Google Cloud SDK

## 方案3：优化Whisper使用（如果必须使用）

如果必须使用Whisper但内存不足，可以尝试：

### 1. 使用更小的模型
- tiny模型：约75MB文件，加载后约200-400MB内存
- 已是最小模型，无法再小

### 2. 按需加载和卸载
代码已实现延迟加载，使用完后可以手动卸载：
```python
# 在代码中添加
if 'whisper_model' in st.session_state:
    del st.session_state.whisper_model
    import gc
    gc.collect()
```

### 3. 增加服务器内存
- 如果可能，增加服务器内存到至少4-8GB

## 当前实现

代码已实现智能切换：
1. **如果Whisper被禁用**（`DISABLE_WHISPER=1`）→ 自动使用speech_recognition
2. **如果Whisper加载失败**（内存不足）→ 自动使用speech_recognition
3. **如果Whisper可用** → 优先使用Whisper，失败时回退到speech_recognition

## 推荐配置（内存不足时）

```bash
# 禁用Whisper，只使用speech_recognition
export DISABLE_WHISPER=1

# 同时禁用OCR（如果也不需要）
export DISABLE_OCR=1

# 启动应用
streamlit run app.py
```

这样配置后：
- ✅ 不占用内存（不加载任何模型）
- ✅ 语音识别功能仍然可用（使用Google API）
- ✅ OCR功能被禁用（如果不需要可以不禁用）

## 检查当前状态

在应用中，可以查看语音识别方法的状态：
- 如果显示 "speech_recognition ✅ 可用（推荐：内存不足时使用）" → 说明已切换到不占用内存的方案
- 如果显示 "Whisper ❌ 加载失败（可能是内存不足）" → 说明已自动切换到speech_recognition

## 总结

**对于内存不足的服务器，推荐使用方案1（speech_recognition）**：
- 设置 `DISABLE_WHISPER=1`
- 确保已安装 `SpeechRecognition` 库
- 确保服务器可以访问Google服务
- 功能完全可用，且不占用内存

