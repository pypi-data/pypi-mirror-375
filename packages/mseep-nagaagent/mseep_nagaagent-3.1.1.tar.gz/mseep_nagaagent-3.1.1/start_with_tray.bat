@echo off
chcp 65001 >nul
title Naga Agent - Tray Mode
cd /d %~dp0
call .venv\Scripts\activate.bat
echo Starting NagaAgent with tray support...
echo Console will be automatically hidden after 3 seconds
echo Console will also be hidden from taskbar
echo Tip: Right-click tray icon to show/hide console window
echo.
echo System check will run automatically on first startup only
echo.
python main.py
pause
