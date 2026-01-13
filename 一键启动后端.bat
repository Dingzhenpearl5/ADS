@echo off
title 智医AI Backend Starter
echo ========================================
echo        智医AI 系统后端一键启动工具
echo ==========================================

:: 检查是否在正确的目录
if not exist "CTAI_flask\app.py" (
    echo [错误] 请在项目根目录下运行此脚本
    pause
    exit
)

echo [1/1] 正在启动后端服务 (Flask)...
echo 提示: 请勿关闭此窗口。

:: 启动 Flask
cd CTAI_flask && call conda activate design39 && python app.py

echo ==========================================
echo 服务已停止
echo ==========================================
pause