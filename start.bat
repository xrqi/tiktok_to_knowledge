@echo off
chcp 65001 >nul
echo ========================================
echo 短视频知识提炼工具 - 启动菜单
echo ========================================
echo.

:MENU
echo 请选择启动方式:
echo 1. GUI界面（桌面应用）
echo 2. Web界面（浏览器访问）
echo 3. 命令行界面
echo 0. 退出
echo.

set /p choice=请输入选项 (0-3):

if "%choice%"=="1" goto GUI
if "%choice%"=="2" goto WEB
if "%choice%"=="3" goto CLI
if "%choice%"=="0" goto END
goto MENU

:GUI
echo.
echo 正在启动GUI界面...
python src\ui\main_window.py
if %errorlevel% neq 0 (
    echo [ERROR] 启动失败！
    pause
    goto MENU
)
goto MENU

:WEB
echo.
echo 正在启动Web界面...
echo 访问地址: http://localhost:5000
echo.
python src\ui\web_app.py
if %errorlevel% neq 0 (
    echo [ERROR] 启动失败！
    pause
    goto MENU
)
goto MENU

:CLI
echo.
echo 正在启动命令行界面...
python src\ui\cli.py --help
if %errorlevel% neq 0 (
    echo [ERROR] 启动失败！
    pause
    goto MENU
)
goto MENU

:END
echo.
echo 再见！
exit /b 0
