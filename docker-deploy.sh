#!/bin/bash

echo "========================================"
echo "知识管理系统 Docker 部署"
echo "========================================"
echo ""

show_menu() {
    echo "请选择操作:"
    echo "1. 构建并启动容器"
    echo "2. 停止容器"
    echo "3. 重启容器"
    echo "4. 查看日志"
    echo "5. 查看容器状态"
    echo "6. 进入容器"
    echo "7. 停止并删除容器"
    echo "8. 备份数据"
    echo "0. 退出"
    echo ""
}

build_start() {
    echo ""
    echo "正在构建并启动容器..."
    docker-compose up -d --build
    echo ""
    echo "容器已启动！"
    echo "访问地址: http://localhost:5000"
    echo ""
}

stop() {
    echo ""
    echo "正在停止容器..."
    docker-compose stop
    echo ""
    echo "容器已停止！"
    echo ""
}

restart() {
    echo ""
    echo "正在重启容器..."
    docker-compose restart
    echo ""
    echo "容器已重启！"
    echo ""
}

logs() {
    echo ""
    echo "正在查看日志 (按 Ctrl+C 退出)..."
    docker-compose logs -f web
}

status() {
    echo ""
    echo "容器状态:"
    docker-compose ps
    echo ""
}

exec() {
    echo ""
    echo "正在进入容器..."
    docker-compose exec web bash
}

down() {
    echo ""
    echo "正在停止并删除容器..."
    docker-compose down
    echo ""
    echo "容器已删除！"
    echo ""
}

backup() {
    echo ""
    echo "正在备份数据..."
    backup_file="backup_$(date +%Y%m%d_%H%M%S).tar.gz"
    tar -czf "$backup_file" data downloads logs
    echo ""
    echo "备份完成: $backup_file"
    echo ""
}

while true; do
    show_menu
    read -p "请输入选项 (0-8): " choice
    
    case $choice in
        1)
            build_start
            ;;
        2)
            stop
            ;;
        3)
            restart
            ;;
        4)
            logs
            ;;
        5)
            status
            ;;
        6)
            exec
            ;;
        7)
            down
            ;;
        8)
            backup
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
