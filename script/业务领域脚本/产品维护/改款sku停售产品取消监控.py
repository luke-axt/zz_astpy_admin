import traceback

from admin.service.DBcore import DBcore
from utils.LogUtils import LogUtils
from utils.dateutil import DatePack


logger = LogUtils.get_logger('改款sku停售产品取消监控')

dbs = DBcore(('192.168.1.80'
                , '3306'
                , 'dba'
                , 'gAAAAABn43OY3qU_OEKerxmpJuXBQthVlZdhkyxEy2yd8Dh1Y-z0rG6IYKlHt1_MCkwbGKVGDp2ZOpjT5_t_sQoop6lWiAwHTw=='
                , 'ast'
                ))


skulist_str = """
CQB-A501-AUXITO-BY-A
"""

sku_list = skulist_str.split('\n')

for sku in sku_list:
    if sku == "":
        continue
    try:
        logger.info(f"更新： {sku}" )
        update_sql = f"UPDATE plan.plan_sku_map SET status='N', update_time= now() WHERE cur_ttsku='{sku}' ;"
        res = dbs.update(update_sql)
        logger.info(f"update - {res}")
    except:
        logger.error(traceback.format_exc())
        exit(1)

