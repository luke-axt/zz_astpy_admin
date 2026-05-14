from 运维管理.MyDeployAdmin import DeployUtil

# 部署前，先执行备份动作
# sh /app/shell/bak_dist.sh

DeployUtil.deploy_dist()
