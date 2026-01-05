@echo off
chcp 65001 >nul
echo ========================================
echo Knowledge Management System Docker Deployment
echo ========================================
echo.

REM Check if Docker is running
docker info >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not running!
    echo.
    echo Please start Docker Desktop first, then run this script again.
    echo.
    echo Steps to start Docker Desktop:
    echo 1. Search for "Docker Desktop" in Windows Start menu
    echo 2. Click to start Docker Desktop
    echo 3. Wait for the Docker icon in system tray to turn green
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)

echo [SUCCESS] Docker is running
echo.

:MENU
echo Please select an operation:
echo 1. Build and start container
echo 2. Stop container
echo 3. Restart container
echo 4. View logs
echo 5. View container status
echo 6. Enter container
echo 7. Stop and remove container
echo 8. Backup data
echo 9. View Docker info
echo 0. Exit
echo.

set /p choice=Please enter option (0-9):

if "%choice%"=="1" goto BUILD_START
if "%choice%"=="2" goto STOP
if "%choice%"=="3" goto RESTART
if "%choice%"=="4" goto LOGS
if "%choice%"=="5" goto STATUS
if "%choice%"=="6" goto EXEC
if "%choice%"=="7" goto DOWN
if "%choice%"=="8" goto BACKUP
if "%choice%"=="9" goto DOCKER_INFO
if "%choice%"=="0" goto END
goto MENU

:BUILD_START
echo.
echo Building and starting container...
docker-compose up -d --build
if %errorlevel% neq 0 (
    echo [ERROR] Build or start failed!
    pause
    goto MENU
)
echo.
echo [SUCCESS] Container started!
echo Access URL: http://localhost:5000
echo.
pause
goto MENU

:STOP
echo.
echo Stopping container...
docker-compose stop
if %errorlevel% neq 0 (
    echo [ERROR] Stop failed!
    pause
    goto MENU
)
echo.
echo [SUCCESS] Container stopped!
echo.
pause
goto MENU

:RESTART
echo.
echo Restarting container...
docker-compose restart
if %errorlevel% neq 0 (
    echo [ERROR] Restart failed!
    pause
    goto MENU
)
echo.
echo [SUCCESS] Container restarted!
echo.
pause
goto MENU

:LOGS
echo.
echo Viewing logs (press Ctrl+C to exit)...
docker-compose logs -f web
pause
goto MENU

:STATUS
echo.
echo Container status:
docker-compose ps
echo.
pause
goto MENU

:EXEC
echo.
echo Entering container...
docker-compose exec web bash
if %errorlevel% neq 0 (
    echo [ERROR] Failed to enter container!
    pause
    goto MENU
)
pause
goto MENU

:DOWN
echo.
echo Stopping and removing container...
docker-compose down
if %errorlevel% neq 0 (
    echo [ERROR] Remove failed!
    pause
    goto MENU
)
echo.
echo [SUCCESS] Container removed!
echo.
pause
goto MENU

:BACKUP
echo.
echo Backing up data...
set backup_file=backup_%date:~0,4%%date:~5,2%%date:~8,2%_%time:~0,2%%time:~3,2%%time:~6,2%.zip
set backup_file=%backup_file: =0%

echo Creating backup: %backup_file%
powershell -Command "Compress-Archive -Path data,downloads,logs -DestinationPath %backup_file% -Force"
if %errorlevel% neq 0 (
    echo [ERROR] Backup failed!
    pause
    goto MENU
)
echo.
echo [SUCCESS] Backup completed: %backup_file%
echo.
pause
goto MENU

:DOCKER_INFO
echo.
echo Docker information:
echo.
docker info
echo.
echo Docker images:
docker images | findstr knowledge
echo.
pause
goto MENU

:END
echo.
echo Goodbye!
exit /b 0
