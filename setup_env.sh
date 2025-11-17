#!/bin/bash
# Linux/Mac脚本：设置虚拟环境

echo "正在创建虚拟环境..."
python3 -m venv venv

echo "正在激活虚拟环境..."
source venv/bin/activate

echo "正在升级pip..."
pip install --upgrade pip

echo "正在安装依赖包..."
pip install -r requirements.txt

echo ""
echo "========================================"
echo "环境配置完成！"
echo "========================================"
echo ""
echo "使用以下命令激活虚拟环境："
echo "  source venv/bin/activate"
echo ""
echo "然后运行应用："
echo "  python -m streamlit run app.py"
echo ""

