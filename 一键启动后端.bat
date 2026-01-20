@echo off
title 直肠肿瘤辅助诊断系统 Backend Starter
echo ========================================
echo        直肠肿瘤辅助诊断系统 后端一键启动工具
echo ==========================================

:: 检查是否在正确的目录
if not exist "ADS_flask\app.py" (
    echo [错误] 请在项目根目录下运行此脚本
    pause
    exit
)

echo [1/1] 正在启动后端服务 (Flask)...
echo 提示: 请勿关闭此窗口。

:: 启动 Flask
cd ADS_flask && call conda activate design39 && python app.py

echo ==========================================
echo 服务已停止
echo ==========================================
pause