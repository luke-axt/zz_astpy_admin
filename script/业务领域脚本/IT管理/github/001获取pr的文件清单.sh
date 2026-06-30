#!/bin/bash
# /d/code/py/zz_astpy_admin/script/业务领域脚本/IT管理/github/001获取pr的文件清单.sh

# 1. 校验输入参数PR号
if [ $# -ne 1 ]; then
    echo "错误：请传入PR编号作为唯一参数，示例：sh 本脚本.sh 231"
    exit 1
fi
PR_NUM="$1"

# 2. 保存执行脚本时的项目根目录
PROJECT_ROOT="$PWD"
echo "当前项目根目录：$PROJECT_ROOT"

# 3. 定义输出根目录，bash统一用正斜杠
OUT_BASE="${PROJECT_ROOT}/zzlc/doc/codereview"

# 4. 检查基础目录是否存在，不存在则终止并提示
if [ ! -d "${OUT_BASE}" ]; then
    echo "============================================="
    echo "错误：目录 ${OUT_BASE} 不存在！"
    echo "请在项目根目录执行此脚本，或手动创建软链接 zzlc/doc/codereview"
    echo "============================================="
    exit 1
fi

# 5. 自动提取仓库项目名（取.git/config里remote origin地址末尾项目名）
PROJECT_NAME=$(git config --get remote.origin.url | sed -E 's/.*\/([^\/]+)\.git$/\1/')
if [ -z "${PROJECT_NAME}" ]; then
    echo "错误：无法获取git仓库项目名称，请检查.git配置"
    exit 1
fi
echo "识别到仓库项目名：${PROJECT_NAME}"

# 6. 拼接最终输出文件路径
OUT_DIR="${OUT_BASE}/${PROJECT_NAME}"
OUT_FILE="${OUT_DIR}/${PR_NUM}_filelist.txt"

# 创建项目子目录（不存在自动新建）
mkdir -p "${OUT_DIR}"


# 7.0 同步远端所有分支，更新本地main
echo "正在拉取远端最新代码，同步main分支..."
git fetch origin
# 切换到main拉取最新（可选二选一）
# 方案1：只更新本地main，不切换工作区（推荐，不改动你当前所在分支）
git update-ref refs/heads/main origin/main

# 7.1 拉取PR临时分支
TEMP_BRANCH="pr-${PR_NUM}-temp"
git fetch origin pull/${PR_NUM}/head:${TEMP_BRANCH} 2>/dev/null

# 8. 输出变更文件并写入目标文件
echo "开始导出PR#${PR_NUM}变更文件清单至：${OUT_FILE}"
git diff --name-only main ${TEMP_BRANCH} > "${OUT_FILE}"

# 9. 清理临时分支
git branch -D ${TEMP_BRANCH}

echo "执行完成，文件清单已生成：${OUT_FILE}"