@echo off
title CTAI Backend Starter
echo ==========================================
echo        CTAI 系统后端一键启动工具
echo ==========================================

:: 检查是否在正确的目录
if not exist "CTAI_flask\app.py" (
    echo [错误] 请在项目根目录下运行此脚本
    pause
    exit
)

echo [1/2] 正在启动 Redis 服务...
:: 尝试启动本地 Redis，如果已作为服务运行则会跳过
start "CTAI-Redis" /min cmd /c "redis-server.exe || echo Redis already running"

echo [2/2] 正在启动后端服务 (Flask + Celery)...
echo 提示: 将打开两个新窗口，请勿关闭它们。

:: 启动 Flask
start "CTAI-Flask" cmd /k "cd CTAI_flask && call conda activate design39 && python app.py"

:: 启动 Celery
:: 使用 -c 1 限制并发数为 1，避免学生服务器内存溢出；使用 eventlet 模式兼容 Windows
start "CTAI-Worker" cmd /k "cd CTAI_flask && call conda activate design39 && celery -A app.celery worker --loglevel=info -P eventlet -c 1"

echo ==========================================
echo 启动指令已发送！
echo - Flask 运行在: http://127.0.0.1:5003
echo - Celery 正在处理异步任务
echo ==========================================
pause