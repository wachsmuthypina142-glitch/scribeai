@echo off
chcp 65001 >nul
title ScribeAI 启动器

echo ========================================
echo       ScribeAI 个人知识管理助手
echo ========================================
echo.

cd /d "%~dp0backend"

if not exist venv (
    echo [1/3] 创建虚拟环境 (Python 3.12)...
    py -3.12 -m venv venv
)

echo [2/3] 升级pip并安装依赖...
call venv\Scripts\activate
python -m pip install --upgrade pip -q
pip install -r requirements.txt -q

echo [3/3] 启动后端服务...
echo.
echo 后端地址: http://localhost:8000
echo API文档:  http://localhost:8000/docs
echo 前端界面: http://localhost:8000 (或直接打开 frontend/index.html)
echo.
echo 按 Ctrl+C 停止服务
echo.

python main.py
