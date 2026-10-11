@echo off
title Apex Sports League Hub
echo ====================================================================
echo  Starting Apex Sports League Hub Backend API Server...
echo ====================================================================
echo.
echo Local API URL:     http://127.0.0.1:8000
echo Swagger UI Docs:   http://127.0.0.1:8000/docs
echo Web Application:   http://127.0.0.1:8000/app/
echo.
echo Press Ctrl+C in this window to stop the server anytime.
echo.
python -m uvicorn backend.main:app --host 127.0.0.1 --port 8000 --reload
pause
