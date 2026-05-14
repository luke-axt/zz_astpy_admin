import os
import sys
import time



i=0
script_dir = os.path.abspath(__file__)
while i<4:
    i=i+1
    script_dir = os.path.dirname(script_dir)
    sys.path.append(script_dir)

import traceback
from utils.LogUtils import LogUtils
from admin.service.EmailService import EmailService


logger = LogUtils.get_logger('zcl开机启动任务')
try:
    logger.info('开始')
    logger.info('延缓120秒启动')
    time.sleep(1)
    EmailService().sendAdmin('zcl开机启动任务-通电通知', '如非本人启动电脑，则代表电脑通电自动启动。')
    logger.info('邮件发送完成')
except Exception:
    errmsg = traceback.format_exc()
    logger.error(f"{errmsg}")
    EmailService().sendAdmin('报错：zcl开机启动任务-通电通知', errmsg)

