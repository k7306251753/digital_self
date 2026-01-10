@echo off
setlocal

echo ===================================================
echo   Digital Self - Unified Startup Script
echo ===================================================
echo.

:: 1. Cleanup
echo [1/5] Stopping existing processes...
taskkill /F /IM python.exe /IM node.exe /IM java.exe >nul 2>&1
echo Done.
echo.

:: 2. Dependencies check
echo [2/5] Checking dependencies...

where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python not found! Please install Python.
    pause
    exit /b
)

where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js not found! Please install Node.js.
    pause
    exit /b
)

where mvn >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Maven not found! Please install Maven.
    pause
    exit /b
)

where ollama >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Ollama not found! Please install Ollama.
    pause
    exit /b
)
echo All dependencies found.
echo.

:: 3. Ollama Model
echo [3/5] Ensuring Ollama model (llama3.2:1b) is available...
echo (This may take a moment if it needs to download)
ollama pull llama3.2:1b
echo Done.
echo.

:: 4. Start Services
echo [4/5] Starting services in separate windows...

echo Starting User Service (Spring Boot)...
start "User Service" cmd /k "cd user_service && mvn spring-boot:run"

echo Starting Backend API (FastAPI)...
start "Backend API" cmd /k "python backend/api_server.py"

echo Starting Web UI (Next.js)...
start "Web UI" cmd /k "cd web_ui && npm run dev"

echo.
echo [5/5] Finalizing...
echo Everything is starting up!
echo.
echo Please wait about 30 seconds for all services to initialize.
echo Access the application at: http://localhost:3000
echo.
echo ===================================================
echo Press any key to close this launcher, or wait 10s...
timeout /t 10 >nul
exit /b
