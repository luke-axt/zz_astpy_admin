#!/bin/bash

log() {
    local msg="[$(date +'%Y-%m-%d %H:%M:%S')] $1"
    # 屏幕输出
    echo "$msg"
    # 写入日志文件，追加模式
    echo "$msg" >> /d/data/deploy.log
}

# ========== 配置区 ==========
LOCAL_PATH="/d/code/javaproject/AST/rpt/rptsql"
REMOTE_PATH="appusr@192.168.1.60:/app/datacenter/uploadPath/rptsql"

# 设置 N：最近多少分钟内修改的文件才部署（默认 10 分钟）
N=10

# ========== 执行逻辑 ==========

# ========================
# 步骤 1：拉取最新代码
# ========================
log "🔄 正在进入项目目录: $LOCAL_PATH"
cd "$LOCAL_PATH" || { echo "❌ 本地路径不存在: $LOCAL_PATH"; exit 1; }

log "📥 正在执行 git pull 获取最新代码..."
if ! git pull; then
    log "❌ git pull 失败！请检查网络、权限或代码冲突。"
    exit 1
fi

# ========================
# 步骤 2：检查是否有最新的文件并推送sql文件到目标路径
# ========================
log "🔍 检查 $LOCAL_PATH 中最近 $N 分钟内修改的文件..."

# 使用 find 查找普通文件（-type f），且修改时间在最近 N 分钟内（-mmin -N）
# 注意：-mmin -N 表示“N 分钟以内”
deployed_any=false

while IFS= read -r -d '' file; do
    filename=$(basename "$file")
    log "   命令: scp \"$file\" \"$REMOTE_PATH\""
    
    if scp "$file" "$REMOTE_PATH"; then
        log "✅ 成功部署: $filename"
        deployed_any=true
    else
        log "❌ 部署失败: $filename"
    fi
done < <(find "$LOCAL_PATH" -type f -mmin -$N -print0)

# 判断是否有文件被部署
if [ "$deployed_any" = false ]; then
    log "ℹ️  无文件在最近 $N 分钟内更新，无需部署。"
fi

log "🔚 部署检查完成。 sql部署"

