@echo off
echo 正在启动 LynAI Platform...
echo.

:: 启动后端
start "LynAI 后端" cmd /k "cd /d C:\Users\39555\projects\lynai-platform\backend && python -m uvicorn app.main:app --reload --port 8000"

:: 等待2秒再启动前端
timeout /t 2 /nobreak >nul

:: 启动前端
start "LynAI 前端" cmd /k "cd /d C:\Users\39555\projects\lynai-platform\frontend && npm run dev"

:: 等待5秒后打开浏览器
timeout /t 5 /nobreak >nul
start http://localhost:3000

echo.
echo 已启动！浏览器将自动打开 http://localhost:3000
echo 如果浏览器没打开，请手动访问 http://localhost:3000
pause
