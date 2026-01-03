@echo off
echo Stopping existing processes...
taskkill /F /IM python.exe /IM node.exe /IM java.exe >nul 2>&1
echo.
echo Ensuring Fast Model is installed...
call ollama pull llama3.2:1b
echo.
echo Starting User Service (Spring Boot)...
start "User Service" cmd /k "cd user_service && mvn spring-boot:run"
echo.
echo Starting Backend...
start "Backend" cmd /k "python backend/api_server.py"
echo.
echo Starting Frontend...
cd web_ui
start "Frontend" cmd /k "npm run dev"
echo.
echo Application starting. Please wait 20 seconds then refresh http://localhost:3000
pause
