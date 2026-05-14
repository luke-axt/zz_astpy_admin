import time

from utils.dateutil import DatePack
from 运维管理.MyDeployAdmin import DeployUtil

while True:
    minute = int(DatePack.parseDatetime2Str(DatePack.getCurtime(), DatePack.MM))
    if (minute > 6 and minute < 50):
        print(DatePack.parseDatetime2Str(DatePack.getCurtime(),DatePack.YYYY_MM_DD_HH_MM_SS) + '  当前属于部署时间窗口，启动部署')
        break

    print(DatePack.parseDatetime2Str(DatePack.getCurtime(), DatePack.YYYY_MM_DD_HH_MM_SS) + '  等待部署窗口，等待5秒')
    time.sleep(5)

DeployUtil.deploy_jar()
