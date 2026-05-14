import traceback

from common.ResultObj import ResultObj
from dwd.DwService import DwService
from utils.dateutil import DatePack
from 运维管理.MyAdmin import MyAdminBase
from 运维管理.业务领域脚本.企业微信.MyQywxService import MyQywxService


class RunDataHis(MyAdminBase):

    def __init__(self,jobname='重跑数仓历史数据'):
        super().__init__(jobname)
        self.qywx = MyQywxService()

    def run_tmp(self,**kwargs):
        dt = '20260204'
        sql = """
UPDATE ast.dml_prod_info
SET erpsku= sku 
WHERE dt=%s;
        """
        stop_dt = '20260209'
        while dt <= stop_dt:
            try:
                res = self.dbs.update(sql,(dt,))
                self.logger.info(f"{dt} - {res}")
            except:
                self.logger.info(f"{dt} - {traceback.format_exc()}")
                return

            dt = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.parseStr2Datetime(dt,DatePack.YYYYMMDD),1),DatePack.YYYYMMDD)

    def run_sale_idx(self, start_dt,stop_dt):
        """
        重新计算两套指标
        """
        table_list = [
            ('dml','dml_idx_sale'),
            ('dml','dml_idx_sale_plan'),
            ('dml','dml_idx_v2_sale'),
            ('dml','dml_idx_v2_sale_multi'),
        ]
        msg_text = f"重新计算两套销量指标数据开始，跑批时间：{start_dt} - {stop_dt}"
        self.logger.info(msg_text)
        res = ResultObj.success()
        for _t in table_list:
            schema,tablename = _t
            dt = start_dt
            while dt <= stop_dt:
                paramJson = f"""[{{"format":"{{dt}}","value":"{dt}"}}]"""
                try:
                    res = DwService(schema).run_job(tablename, paramJson)
                    self.logger.info(f"{dt} - {res} - {DatePack.getCurtime()}")
                except:
                    self.logger.error(f"{dt} - {traceback.format_exc()} - {DatePack.getCurtime()}")
                    res = ResultObj.error(ResultObj.FATAL_ERROR, traceback.format_exc())

                if res.is_fail():
                    break

                dt = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.parseStr2Datetime(dt, DatePack.YYYYMMDD), 1),
                                                DatePack.YYYYMMDD)
            if res.is_fail():
                break

        if res.is_fail():
            self.qywx.api_sent_msg_to_user(f"，跑批异常，请及时处理。RunDataHis.run_sale_idx，{msg_text}")
        else:
            self.qywx.api_sent_msg_to_user(f"正常完成：RunDataHis.run_sale_idx，{msg_text}")

