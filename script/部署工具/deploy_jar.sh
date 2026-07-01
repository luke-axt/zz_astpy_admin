#!/bin/bash

# ========================
# 配置区（请按需修改）
# ========================
LOCAL_PATH="/d/code/javaproject/AST"
LOCAL_JAR_PATH="$LOCAL_PATH/ruoyi-admin/target/ast.jar" 
REMOTE_USER="appusr"
REMOTE_HOST="192.168.1.60"
REMOTE_DIR="/app/datacenter"
REMOTE_RESTART_SCRIPT="$REMOTE_DIR/restart.sh"

# ========================
# 函数：打印日志
# ========================
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] $1"
}

# ========== 执行逻辑 ==========
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

# 1. Maven 打包（生产环境）
log "🧱 开始 Maven 打包: mvn clean install -Pprod"
mvn clean install -Pprod --batch-mode || error_exit "Maven 打包失败！"

========================
主流程
========================

1. 检查本地 JAR 是否存在
if [ ! -f "$LOCAL_JAR_PATH" ]; then
    log "❌ 错误：本地 JAR 文件不存在: $LOCAL_JAR_PATH"
    exit 1
fi

# 2. 本地备份（带时间戳）
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
LOCAL_BAK="${LOCAL_JAR_PATH}.bak${TIMESTAMP}"
log "📁 本地备份 JAR 包到: $LOCAL_BAK"
cp "$LOCAL_JAR_PATH" "$LOCAL_BAK"

# 3. 清理旧的备份（保留最近5个）
log "🧹 清理旧的本地备份（保留最近5个）"
ls -t "${LOCAL_JAR_PATH}.bak"* 2>/dev/null | tail -n +6 | xargs -r rm

# 4. 上传 JAR 到服务器
log "📤 上传 JAR 包到 $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"
scp "$LOCAL_JAR_PATH" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" || {
    log "❌ 上传失败！"
    exit 1
}

# 5. 远程执行重启脚本
log "🔄 通过 SSH 远程执行重启脚本..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" "bash $REMOTE_RESTART_SCRIPT" || {
    log "❌ 远程重启失败！"
    exit 1
}

log "✅ 部署与重启完成！"