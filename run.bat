@REM @echo off
@REM setlocal enabledelayedexpansion


@REM :: 请求管理员权限
@REM >nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
@REM if %errorlevel% neq 0 (
@REM     echo 需要管理员权限，正在重新启动...
@REM     powershell Start-Process -FilePath "%0" -Verb RunAs
@REM     exit
@REM )

@REM echo === 防火墙临时规则 ===
@REM netsh advfirewall firewall add rule name="LogAnalyzer-Backend" dir=in action=allow protocol=TCP localport=8000
@REM netsh advfirewall firewall add rule name="LogAnalyzer-Frontend" dir=in action=allow protocol=TCP localport=3000

@REM echo === 启动服务 ===
@REM start "BACKEND" cmd /k "python backend/main.py"
@REM cd frontend
@REM start "FRONTEND" cmd /k "npm run dev"

@REM echo === 退出清理 ===
@REM echo 按任意键关闭服务并恢复防火墙...
@REM pause >nul

@REM netsh advfirewall firewall delete rule name="LogAnalyzer-Backend"
@REM netsh advfirewall firewall delete rule name="LogAnalyzer-Frontend"
@REM taskkill /F /IM python.exe >nul 2>&1
@REM taskkill /F /IM node.exe >nul 2>&1


@REM echo === 清理旧进程 ===

@REM taskkill /F /IM node.exe >nul 2>&1
@REM timeout /t 2 >nul

@REM echo === 端口冲突检查 ===
@REM :check_port
@REM netstat -ano | findstr ":%BACKEND_PORT%" >nul
@REM if %errorlevel% equ 0 (
@REM    echo 端口 %BACKEND_PORT% 被占用，尝试释放...
@REM    for /f "tokens=5" %%a in ('netstat -ano ^| findstr ":%BACKEND_PORT%"') do taskkill /F /PID %%a >nul
@REM    timeout /t 2 >nul
@REM    goto :check_port
@REM )

@REM echo === 安装Python依赖 ===
@REM python -m pip install -r backend/requirements.txt
@REM if %errorlevel% neq 0 (
@REM    echo [错误] Python依赖安装失败
@REM    exit /b 1
@REM )

@REM echo === 启动后端服务 ===
@REM start "BACKEND" cmd /k "uvicorn backend.main:app --host 0.0.0.0 --port %BACKEND_PORT%"
@REM echo 等待后端初始化...
@REM timeout /t 10 >nul

@REM echo === 安装前端依赖 ===
@REM cd frontend
@REM npm install --legacy-peer-deps --force
@REM if %errorlevel% neq 0 (
@REM    echo [错误] npm依赖安装失败
@REM    exit /b 1
@REM )
@REM npm audit fix --force

@REM echo === 启动前端服务 ===
@REM start "FRONTEND_DEV" cmd /k "npm run dev -- --port %FRONTEND_PORT%"
@REM start "ELECTRON" cmd /k "npm run electron:dev"

@REM echo === 访问地址 ===
@REM echo 后端API文档: http://localhost:%BACKEND_PORT%/docs
@REM echo 前端调试地址: http://localhost:%FRONTEND_PORT%/
@REM echo Electron窗口应该会自动打开...

@REM exit /b 0


@echo off
setlocal enabledelayedexpansion

:: 自动提权
>nul 2>&1 "%SYSTEMROOT%\system32\cacls.exe" "%SYSTEMROOT%\system32\config\system"
if %errorlevel% neq 0 (
    echo 正在获取管理员权限...
    powershell Start-Process -FilePath "%0" -Verb RunAs
    exit
)

:: 环境配置
set BACKEND_PORT=8000
set FRONTEND_PORT=3000

:: 清理进程
taskkill /F /IM uvicorn.exe >nul 2>&1
taskkill /F /IM node.exe >nul 2>&1

:: 安装后端依赖
cd backend
python -m pip install -r requirements.txt
if errorlevel 1 exit /b 1

:: 启动后端
start "BACKEND" cmd /k "uvicorn main:app --host 0.0.0.0 --port %BACKEND_PORT%"

:: 安装前端依赖
cd ../frontend
npm install --force
if errorlevel 1 exit /b 1

:: 启动前端
start "FRONTEND" cmd /k "npm run dev -- --port %FRONTEND_PORT%"
timeout /t 5
start "ELECTRON" cmd /k "npm run electron:dev"

exit /b 0