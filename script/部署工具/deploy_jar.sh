#!/bin/bash
# ========================
# 配置区（请按需修改）
# 这是一个在windows环境，在git bash上运行的shell脚本
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
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    # 屏幕输出
    echo "$msg"
    # 写入日志文件，追加模式
    echo "$msg" >> /d/data/deploy.log
}

# 新增：失败退出函数（原脚本缺失，核心修复点）
error_exit() {
    log "❌ $1"
    exit 1
}

# ========== 执行逻辑 ==========
# ========================
# 步骤 1：拉取最新代码
# ========================
echo "🔄 正在进入项目目录: $LOCAL_PATH"
cd "$LOCAL_PATH" || error_exit "本地路径不存在: $LOCAL_PATH"

# 判断旧jar存在则删除
if [ -f "$LOCAL_JAR_PATH" ]; then
    log "🗑️ 检测到旧jar包，执行删除: $LOCAL_JAR_PATH"
    rm -f "$LOCAL_JAR_PATH"
fi

echo "📥 正在执行 git pull 获取最新代码..."
if ! git pull; then
    error_exit "git pull 失败！请检查网络、权限或代码冲突。"
fi

# 1. Maven 打包（生产环境）
log "🧱 开始 Maven 打包: mvn clean install -Pprod --batch-mode"
# 构建失败直接调用error_exit终止脚本
mvn clean install -Pprod --batch-mode || error_exit "Maven 打包失败！"

# ========================
# 主流程
# ========================
# 检查本地 JAR 是否存在
if [ ! -f "$LOCAL_JAR_PATH" ]; then
    error_exit "本地 JAR 文件不存在: $LOCAL_JAR_PATH"
fi

# 本地备份（带时间戳）
TIMESTAMP=$(date +"%Y%m%d%H%M%S")
LOCAL_BAK="${LOCAL_JAR_PATH}.bak${TIMESTAMP}"
log "📁 本地备份 JAR 包到: $LOCAL_BAK"
cp "$LOCAL_JAR_PATH" "$LOCAL_BAK"

# 清理旧的备份（保留最近5个）
log "🧹 清理旧的本地备份（保留最近5个）"
bak_list=$(ls -t -- "${LOCAL_JAR_PATH}.bak"* 2>/dev/null)
bak_count=$(echo "$bak_list" | wc -l)
log "当前备份文件总数：${bak_count}"
ls -t "${LOCAL_JAR_PATH}.bak"* 2>/dev/null | tail -n +6 | xargs -r rm

# 上传 JAR 到服务器
log "📤 上传 JAR 包到 $REMOTE_USER@$REMOTE_HOST:$REMOTE_DIR/"
scp "$LOCAL_JAR_PATH" "${REMOTE_USER}@${REMOTE_HOST}:${REMOTE_DIR}/" || error_exit "上传失败！"

# 远程执行重启脚本
log "🔄 通过 SSH 远程执行重启脚本..."
ssh "${REMOTE_USER}@${REMOTE_HOST}" "bash $REMOTE_RESTART_SCRIPT" || error_exit "远程重启失败！"

log "✅ 部署与重启完成！ jar部署"