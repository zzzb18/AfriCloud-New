@echo off
REM Windows批处理脚本：运行应用

echo 正在激活虚拟环境...
call venv\Scripts\activate.bat

echo 正在启动Streamlit应用...
python -m streamlit run app.py

pause

