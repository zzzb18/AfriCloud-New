#!/bin/bash
# Linux/Mac脚本：运行应用

echo "正在激活虚拟环境..."
source venv/bin/activate

echo "正在启动Streamlit应用..."
python -m streamlit run app.py

