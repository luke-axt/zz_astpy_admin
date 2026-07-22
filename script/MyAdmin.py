import traceback

from admin.service.DBcore import DBcore
from common.BaseObj import AdminBase
from common.ResultObj import ResultObj
from utils.LogUtils import LogUtils
from zzlc.script.业务领域脚本.企业微信.MyQywxService import MyQywxService


class MyAdminBase(AdminBase):

    def __init__(self,jobname):
        super().__init__()
        self.set_dbs(DBcore(('192.168.1.79'
                , '3306'
                , 'dba'
                , 'gAAAAABn43OY3qU_OEKerxmpJuXBQthVlZdhkyxEy2yd8Dh1Y-z0rG6IYKlHt1_MCkwbGKVGDp2ZOpjT5_t_sQoop6lWiAwHTw=='
                , 'ast'
                )))
        self.logger = LogUtils.get_logger(jobname)
        self.smb62_info = {'server': '192.168.1.62', 'username': 'zhengcilin', 'password': 'gAAAAABorSObQBLzfTR5PnGOlQGATacMGgx16nNPcOmi6UkmzhSTwyDGUkbpev8C4Z8T-jhdV6Xr1Npl9QS8A1kELHsaUAkqdw=='}
        self.qywx = MyQywxService()

    def run(self, **kwargs) -> ResultObj:
        """
        通用的作业启动方法
        :return:
        """
        try:
            res = self.action(**kwargs)
            self.logger.info(f"运行无异常，结束")
        except:
            errmsg = f'运行异常：{traceback.format_exc()}'
            self.logger.error(f"{errmsg}")
            res = ResultObj.error(ResultObj.FATAL_ERROR,errmsg)
        return res

    def action(self, **kwargs) -> ResultObj:
        pass
