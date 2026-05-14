import traceback

from admin.service.DBcore import DBcore
from utils.LogUtils import LogUtils


logger = LogUtils.get_logger('维护改款sku映射')

dbs = DBcore(('192.168.1.79'
                , '3306'
                , 'dba'
                , 'gAAAAABn43OY3qU_OEKerxmpJuXBQthVlZdhkyxEy2yd8Dh1Y-z0rG6IYKlHt1_MCkwbGKVGDp2ZOpjT5_t_sQoop6lWiAwHTw=='
                , 'ast'
                ))


oldskustr = """
DY-ATO-JS02-AUTOONE-BB-B
"""

newskustr="""
DY-ATO-JS02-AUTOONE-BB-C
"""

old_sku_list = oldskustr.split('\n')
new_sku_list = newskustr.split('\n')

if len(old_sku_list) != len(new_sku_list):
    logger.error(f"整理的sku信息不准确，新旧个数不相等，程序退出")
    exit(1)

i=0
sku_list = []
while i<len(old_sku_list):
    oldsku = old_sku_list[i]
    newsku = new_sku_list[i]
    i += 1
    if oldsku == newsku:
        logger.error(f"{oldsku} - {newsku}  相同，跳过。")
        continue
    if oldsku[0:len(newsku)-2] != newsku[0:-2]:
        logger.error(f"{oldsku} - {newsku}  维护的sku关系不准确，程序退出。")
        exit(1)
    if oldsku != '':
        sku_list.append({'oldsku':oldsku,'newsku':newsku})

logger.info(f"检查结束，无异常，正式执行-------------------------------------------------------------")

i = 0
for item in sku_list:
    try:
        logger.info(f"{item['oldsku']} -->> {item['newsku']}")
        update_sql = f"UPDATE plan.plan_sku_map SET cur_ttsku='{item['newsku']}', update_time= now(), status='Y' WHERE cur_ttsku='{item['oldsku']}' ;"
        res = dbs.update(update_sql)
        logger.info(f"update - {res}")
        insert_sql = f"INSERT INTO plan.plan_sku_map (ttsku, cur_ttsku, update_time, status) VALUES('{item['oldsku']}', '{item['newsku']}', now(), 'Y');"
        res = dbs.insert(insert_sql)
        logger.info(f"insert - {res}")
        i += 1
    except:
        logger.error(traceback.format_exc())
        exit(1)

logger.info(f"全部处理完成，共处理 {i} 个改款sku，请核对。")
