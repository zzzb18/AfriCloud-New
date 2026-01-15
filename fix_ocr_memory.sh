#!/bin/bash
# OCR内存优化快速修复脚本

echo "=========================================="
echo "OCR内存优化快速修复脚本"
echo "=========================================="
echo ""

# 检测系统
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    OS="other"
fi

echo "检测到系统: $OS"
echo ""

# 检查当前内存
echo "当前内存使用情况:"
if command -v free &> /dev/null; then
    free -h
elif command -v vm_stat &> /dev/null; then
    vm_stat | head -5
fi
echo ""

# 选项菜单
echo "请选择修复方案:"
echo "1. 禁用OCR（如果不需要OCR功能）"
echo "2. 安装并使用Tesseract OCR（推荐，轻量级）"
echo "3. 只使用英文EasyOCR（减少内存）"
echo "4. 安装并使用PaddleOCR（中等内存）"
echo "5. 查看当前OCR配置"
echo "6. 退出"
echo ""

read -p "请输入选项 (1-6): " choice

case $choice in
    1)
        echo ""
        echo "设置环境变量: DISABLE_OCR=1"
        export DISABLE_OCR=1
        echo "export DISABLE_OCR=1" >> ~/.bashrc
        echo "✅ OCR已禁用"
        echo ""
        echo "启动应用:"
        echo "streamlit run app.py"
        ;;
    2)
        echo ""
        echo "安装Tesseract OCR..."
        
        if [ "$OS" == "linux" ]; then
            if command -v apt-get &> /dev/null; then
                sudo apt-get update
                sudo apt-get install -y tesseract-ocr tesseract-ocr-eng tesseract-ocr-chi-sim
            elif command -v yum &> /dev/null; then
                sudo yum install -y tesseract tesseract-langpack-eng tesseract-langpack-chi_sim
            fi
        elif [ "$OS" == "macos" ]; then
            if command -v brew &> /dev/null; then
                brew install tesseract
            else
                echo "❌ 请先安装Homebrew: https://brew.sh"
                exit 1
            fi
        fi
        
        echo ""
        echo "安装Python依赖..."
        pip install pytesseract pillow
        
        echo ""
        echo "设置环境变量..."
        export OCR_ENGINE=tesseract
        export DISABLE_EASYOCR=1
        echo "export OCR_ENGINE=tesseract" >> ~/.bashrc
        echo "export DISABLE_EASYOCR=1" >> ~/.bashrc
        
        echo ""
        echo "✅ Tesseract OCR已配置"
        echo ""
        echo "验证安装:"
        tesseract --version
        echo ""
        echo "启动应用:"
        echo "streamlit run app.py"
        ;;
    3)
        echo ""
        echo "配置只使用英文EasyOCR..."
        export ENABLE_CHINESE_OCR=false
        echo "export ENABLE_CHINESE_OCR=false" >> ~/.bashrc
        echo "✅ 已配置只使用英文EasyOCR（减少内存占用）"
        echo ""
        echo "启动应用:"
        echo "streamlit run app.py"
        ;;
    4)
        echo ""
        echo "安装PaddleOCR..."
        pip install paddlepaddle paddleocr
        
        echo ""
        echo "设置环境变量..."
        export OCR_ENGINE=paddleocr
        export DISABLE_EASYOCR=1
        echo "export OCR_ENGINE=paddleocr" >> ~/.bashrc
        echo "export DISABLE_EASYOCR=1" >> ~/.bashrc
        
        echo ""
        echo "✅ PaddleOCR已配置"
        echo ""
        echo "启动应用:"
        echo "streamlit run app.py"
        ;;
    5)
        echo ""
        echo "当前OCR配置:"
        echo "DISABLE_OCR: ${DISABLE_OCR:-未设置}"
        echo "OCR_ENGINE: ${OCR_ENGINE:-未设置（默认EasyOCR）}"
        echo "ENABLE_CHINESE_OCR: ${ENABLE_CHINESE_OCR:-未设置（默认false）}"
        echo ""
        echo "检查OCR库安装情况:"
        
        if python -c "import easyocr" 2>/dev/null; then
            echo "✅ EasyOCR: 已安装"
        else
            echo "❌ EasyOCR: 未安装"
        fi
        
        if python -c "import pytesseract" 2>/dev/null; then
            echo "✅ Tesseract (Python): 已安装"
            if command -v tesseract &> /dev/null; then
                echo "   Tesseract版本: $(tesseract --version | head -1)"
            else
                echo "   ⚠️  Tesseract未安装或不在PATH中"
            fi
        else
            echo "❌ Tesseract (Python): 未安装"
        fi
        
        if python -c "from paddleocr import PaddleOCR" 2>/dev/null; then
            echo "✅ PaddleOCR: 已安装"
        else
            echo "❌ PaddleOCR: 未安装"
        fi
        ;;
    6)
        echo "退出"
        exit 0
        ;;
    *)
        echo "无效选项"
        exit 1
        ;;
esac

echo ""
echo "=========================================="
echo "完成！"
echo "=========================================="
