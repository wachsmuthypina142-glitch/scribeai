#!/bin/bash
cd "$(dirname \"$0\")/backend"

if [ ! -d "venv" ]; then
    echo "[1/3] 创建虚拟环境..."
    python -m venv venv
fi

echo "[2/3] 激活虚拟环境并安装依赖..."
source venv/bin/activate
pip install -r requirements.txt -q

echo "[3/3] 启动后端服务..."
echo ""
echo "后端地址: http://localhost:8000"
echo "API文档:  http://localhost:8000/docs"
echo "前端界面: 直接用浏览器打开 frontend/index.html"
echo ""
echo "按 Ctrl+C 停止服务"
echo ""

python main.py
