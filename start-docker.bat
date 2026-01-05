@echo off
REM Quick start script for Docker deployment
chcp 65001 >nul

echo Checking Docker status...
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop first.
    pause
    exit /b 1
)

echo [OK] Docker is running
echo.
echo Building and starting container...
docker-compose up -d --build

if %errorlevel% neq 0 (
    echo [ERROR] Failed to start container!
    pause
    exit /b 1
)

echo.
echo [SUCCESS] Container is running!
echo.
echo Access the application at: http://localhost:5000
echo.
echo To view logs, run: docker-compose logs -f web
echo To stop the container, run: docker-compose down
echo.
pause
