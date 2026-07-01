#!/bin/bash

set -e  # 可选：遇到错误立即退出（但我们会手动控制 git pull 的错误）

# ========================
# 配置区
# ========================
LOCAL_PATH="/d/app/astpy"      # 本地代码路径（WSL 下对应 D:\app\astpy）
SERVER_PATH="D:\\app\\astpy"     # 远程服务器目标路径
USER="usr_ssh"                     # SSH 用户名

SERVER_IP_LIST=("192.168.1.63" "192.168.1.65" "192.168.1.67")
# SERVER_IP_LIST=("192.168.1.65")
DIR_LIST=(
    "admin" "client" "common" "CoreBussiness" "dwd" "ETL" "rpa" "rpt" "statics" "task" "utils" "辅助工具"
)

# ========================
# 步骤 1：拉取最新代码
# ========================
echo "🔄 正在进入项目目录: $LOCAL_PATH"
cd "$LOCAL_PATH" || { echo "❌ 本地路径不存在: $LOCAL_PATH"; exit 1; }

echo "📥 正在执行 git pull 获取最新代码..."
if ! git pull; then
    echo "❌ git pull 失败！请检查网络、权限或代码冲突。"
    exit 1
fi

echo "✅ 代码拉取成功！"

# ========================
# 步骤 2：部署到各服务器
# ========================
for server_ip in "${SERVER_IP_LIST[@]}"; do
    echo "🚀 开始部署到服务器: $server_ip"

    for dir in "${DIR_LIST[@]}"; do
        echo "📤 正在同步目录: $dir 到 $server_ip"
        if scp -r "$LOCAL_PATH/$dir" "$USER@$server_ip:$SERVER_PATH/"; then
            echo "✅ $dir 部署成功"
        else
            echo "❌ $dir 部署失败！终止部署，请注意！！！"
            exit 1
            # 可选择继续或中断：这里选择继续其他目录
        fi
    done

    echo "✅ 服务器 $server_ip 部署完成！----------------------------------------"
done

echo "🎉 所有服务器部署完毕！"