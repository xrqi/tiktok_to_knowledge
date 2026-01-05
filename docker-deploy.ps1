# 知识管理系统 Docker 部署脚本 (PowerShell版本)

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "知识管理系统 Docker 部署" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查Docker是否运行
function Test-DockerRunning {
    try {
        $null = docker info 2>&1
        return $true
    } catch {
        return $false
    }
}

if (-not (Test-DockerRunning)) {
    Write-Host "[错误] Docker未运行！" -ForegroundColor Red
    Write-Host ""
    Write-Host "请先启动Docker Desktop，然后再运行此脚本。" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "启动Docker Desktop的步骤：" -ForegroundColor Yellow
    Write-Host "1. 在Windows开始菜单中搜索 'Docker Desktop'" -ForegroundColor White
    Write-Host "2. 点击启动Docker Desktop" -ForegroundColor White
    Write-Host "3. 等待Docker图标在系统托盘中变为绿色" -ForegroundColor White
    Write-Host "4. 重新运行此脚本" -ForegroundColor White
    Write-Host ""
    Read-Host "按回车键退出"
    exit 1
}

Write-Host "[成功] Docker正在运行" -ForegroundColor Green
Write-Host ""

function Show-Menu {
    Write-Host "请选择操作:" -ForegroundColor Cyan
    Write-Host "1. 构建并启动容器" -ForegroundColor White
    Write-Host "2. 停止容器" -ForegroundColor White
    Write-Host "3. 重启容器" -ForegroundColor White
    Write-Host "4. 查看日志" -ForegroundColor White
    Write-Host "5. 查看容器状态" -ForegroundColor White
    Write-Host "6. 进入容器" -ForegroundColor White
    Write-Host "7. 停止并删除容器" -ForegroundColor White
    Write-Host "8. 备份数据" -ForegroundColor White
    Write-Host "9. 查看Docker信息" -ForegroundColor White
    Write-Host "0. 退出" -ForegroundColor White
    Write-Host ""
}

function Build-Start {
    Write-Host ""
    Write-Host "正在构建并启动容器..." -ForegroundColor Yellow
    docker-compose up -d --build
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 构建或启动失败！" -ForegroundColor Red
        Read-Host "按回车键继续"
        return
    }
    Write-Host ""
    Write-Host "[成功] 容器已启动！" -ForegroundColor Green
    Write-Host "访问地址: http://localhost:5000" -ForegroundColor Cyan
    Write-Host ""
    Read-Host "按回车键继续"
}

function Stop-Container {
    Write-Host ""
    Write-Host "正在停止容器..." -ForegroundColor Yellow
    docker-compose stop
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 停止容器失败！" -ForegroundColor Red
        Read-Host "按回车键继续"
        return
    }
    Write-Host ""
    Write-Host "[成功] 容器已停止！" -ForegroundColor Green
    Write-Host ""
    Read-Host "按回车键继续"
}

function Restart-Container {
    Write-Host ""
    Write-Host "正在重启容器..." -ForegroundColor Yellow
    docker-compose restart
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 重启容器失败！" -ForegroundColor Red
        Read-Host "按回车键继续"
        return
    }
    Write-Host ""
    Write-Host "[成功] 容器已重启！" -ForegroundColor Green
    Write-Host ""
    Read-Host "按回车键继续"
}

function Show-Logs {
    Write-Host ""
    Write-Host "正在查看日志 (按 Ctrl+C 退出)..." -ForegroundColor Yellow
    docker-compose logs -f web
    Read-Host "按回车键继续"
}

function Show-Status {
    Write-Host ""
    Write-Host "容器状态:" -ForegroundColor Cyan
    docker-compose ps
    Write-Host ""
    Read-Host "按回车键继续"
}

function Enter-Container {
    Write-Host ""
    Write-Host "正在进入容器..." -ForegroundColor Yellow
    docker-compose exec web bash
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 进入容器失败！" -ForegroundColor Red
        Read-Host "按回车键继续"
        return
    }
    Read-Host "按回车键继续"
}

function Remove-Container {
    Write-Host ""
    Write-Host "正在停止并删除容器..." -ForegroundColor Yellow
    docker-compose down
    if ($LASTEXITCODE -ne 0) {
        Write-Host "[错误] 删除容器失败！" -ForegroundColor Red
        Read-Host "按回车键继续"
        return
    }
    Write-Host ""
    Write-Host "[成功] 容器已删除！" -ForegroundColor Green
    Write-Host ""
    Read-Host "按回车键继续"
}

function Backup-Data {
    Write-Host ""
    Write-Host "正在备份数据..." -ForegroundColor Yellow
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backup_$timestamp.zip"

    try {
        Compress-Archive -Path "data", "downloads", "logs" -DestinationPath $backupFile -Force
        Write-Host ""
        Write-Host "[成功] 备份完成: $backupFile" -ForegroundColor Green
    } catch {
        Write-Host "[错误] 备份失败: $_" -ForegroundColor Red
    }
    Write-Host ""
    Read-Host "按回车键继续"
}

function Show-DockerInfo {
    Write-Host ""
    Write-Host "Docker信息:" -ForegroundColor Cyan
    Write-Host ""
    docker info
    Write-Host ""
    Write-Host "Docker镜像:" -ForegroundColor Cyan
    docker images | Select-String "knowledge"
    Write-Host ""
    Read-Host "按回车键继续"
}

while ($true) {
    Show-Menu
    $choice = Read-Host "请输入选项 (0-9)"

    switch ($choice) {
        "1" { Build-Start }
        "2" { Stop-Container }
        "3" { Restart-Container }
        "4" { Show-Logs }
        "5" { Show-Status }
        "6" { Enter-Container }
        "7" { Remove-Container }
        "8" { Backup-Data }
        "9" { Show-DockerInfo }
        "0" {
            Write-Host ""
            Write-Host "再见！" -ForegroundColor Green
            exit 0
        }
        default {
            Write-Host ""
            Write-Host "[错误] 无效选项，请重新输入！" -ForegroundColor Red
            Write-Host ""
            Read-Host "按回车键继续"
        }
    }

    Clear-Host
}
