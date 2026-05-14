import time

from utils.dateutil import DatePack
from 运维管理.MyAdmin import MyAdminBase
from 运维管理.业务领域脚本.企业微信.MyQywxService import MyQywxService


class JiufangJobOffline(MyAdminBase):

    def __init__(self,jobname='九方作业下线'):
        super().__init__(jobname)
        self.qywx = MyQywxService()

    def job_offline(self):
        """
        写个自动脚本更新java 166 作业为禁用，status=1（采集九方库存），周六中午12点更新
写个python jobid =32 标记为禁用（老九方库存odl）周日上午更新

        """
        msg_user_id = 'gtd|itZhuGuan-ChenHengHuan'
        while True:
            cur_time = DatePack.parseDatetime2Str(DatePack.getCurtime(),DatePack.YYYY_MM_DD_HH_MM_SS)
            if cur_time > '2026-03-28 13:00:00':
                javasql = """
                UPDATE astdc.sys_job
                SET status='1'
                WHERE job_id=166;
                        """
                self.dbs.update(javasql)
                self.qywx.api_sent_msg_to_user(f"java采集九方库存已下线。",msg_user_id)
                break
            self.logger.info(f"等待更新java采集九方库存下线")
            time.sleep(1200)


        while True:
            cur_time = DatePack.parseDatetime2Str(DatePack.getCurtime(),DatePack.YYYY_MM_DD_HH_MM_SS)
            if cur_time > '2026-03-29 10:00:00':
                pysql = """
                UPDATE astdc.dc_job_info
                SET is_valid='N'
                WHERE jobid=32;
                """
                self.dbs.update(pysql)
                self.qywx.api_sent_msg_to_user(f"python 旧九方库存odl作业已下线。",msg_user_id)
                break
            self.logger.info(f"等待旧九方库存odl作业下线")
            time.sleep(1200)


JiufangJobOffline().job_offline()

