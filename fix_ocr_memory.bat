@echo off
REM OCR内存优化快速修复脚本 (Windows版本)

echo ==========================================
echo OCR内存优化快速修复脚本
echo ==========================================
echo.

echo 请选择修复方案:
echo 1. 禁用OCR（如果不需要OCR功能）
echo 2. 只使用英文EasyOCR（减少内存）
echo 3. 查看当前OCR配置
echo 4. 退出
echo.

set /p choice="请输入选项 (1-4): "

if "%choice%"=="1" (
    echo.
    echo 设置环境变量: DISABLE_OCR=1
    setx DISABLE_OCR "1"
    echo ✅ OCR已禁用
    echo.
    echo 启动应用:
    echo streamlit run app.py
    goto :end
)

if "%choice%"=="2" (
    echo.
    echo 配置只使用英文EasyOCR...
    setx ENABLE_CHINESE_OCR "false"
    echo ✅ 已配置只使用英文EasyOCR（减少内存占用）
    echo.
    echo 启动应用:
    echo streamlit run app.py
    goto :end
)

if "%choice%"=="3" (
    echo.
    echo 当前OCR配置:
    echo DISABLE_OCR: %DISABLE_OCR%
    echo ENABLE_CHINESE_OCR: %ENABLE_CHINESE_OCR%
    echo.
    echo 检查OCR库安装情况:
    python -c "import easyocr; print('✅ EasyOCR: 已安装')" 2>nul || echo ❌ EasyOCR: 未安装
    python -c "import pytesseract; print('✅ Tesseract (Python): 已安装')" 2>nul || echo ❌ Tesseract (Python): 未安装
    python -c "from paddleocr import PaddleOCR; print('✅ PaddleOCR: 已安装')" 2>nul || echo ❌ PaddleOCR: 未安装
    goto :end
)

if "%choice%"=="4" (
    echo 退出
    exit /b 0
)

echo 无效选项

:end
echo.
echo ==========================================
echo 完成！
echo ==========================================
pause
