@echo off
title SecureBox SOC Launcher
cd /d C:\Projects\SecureBox

:: Start VS Code (optional)
start code C:\Projects\SecureBox

:: Start the main SOC Orchestrator (handles Flask + Streamlit internally)
python Launch_soc_testing_center.py

echo.
echo ✅ SecureBox SOC started successfully!
pause
