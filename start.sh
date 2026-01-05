#!/bin/bash

echo "========================================"
echo "短视频知识提炼工具 - 启动菜单"
echo "========================================"
echo ""

show_menu() {
    echo "请选择启动方式:"
    echo "1. GUI界面（桌面应用）"
    echo "2. Web界面（浏览器访问）"
    echo "3. 命令行界面"
    echo "0. 退出"
    echo ""
}

gui() {
    echo ""
    echo "正在启动GUI界面..."
    python src/ui/main_window.py
}

web() {
    echo ""
    echo "正在启动Web界面..."
    echo "访问地址: http://localhost:5000"
    echo ""
    python src/ui/web_app.py
}

cli() {
    echo ""
    echo "正在启动命令行界面..."
    python src/ui/cli.py --help
}

while true; do
    show_menu
    read -p "请输入选项 (0-3): " choice
    
    case $choice in
        1)
            gui
            ;;
        2)
            web
            ;;
        3)
            cli
            ;;
        0)
            echo ""
            echo "再见！"
            exit 0
            ;;
        *)
            echo ""
            echo "无效选项，请重新输入！"
            echo ""
            ;;
    esac
    
    echo "按任意键继续..."
    read -n 1
    clear
done
