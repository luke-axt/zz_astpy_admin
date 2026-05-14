import os

import pandas as pd

from admin.service.DBcore import DBcore
from utils.dateutil import DatePack


dbs = DBcore(('192.168.1.80'
                , '3306'
                , 'dba'
                , 'gAAAAABn43OY3qU_OEKerxmpJuXBQthVlZdhkyxEy2yd8Dh1Y-z0rG6IYKlHt1_MCkwbGKVGDp2ZOpjT5_t_sQoop6lWiAwHTw=='
                , 'ast'
                ))

dt = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.getCurtime(),-2),DatePack.YYYYMMDD)
print(f"dt - {dt}")
sql1 = f"""
with t_sku as (
select t.sku ,t1.classify,ifnull(psm.cur_ttsku,t.sku)  as cur_sku
  from astdc.tt_product_info t 
  join astdc.tt_prod_rpa t1 
    on t.sku = t1.sku 
  left join plan.plan_sku_map psm 
    on t.sku = psm.ttsku 
 where t.developerName = '产品开发-吴宇迪' and ifnull(t.isDelete,'0') = '0'
)
select d1.classify,d.dt,d.warehouse_id ,d1.cur_sku ,sum(d.qty_mth) as qty_mth
  from ast.dml_idx_sale_mth d
  join t_sku d1
    on d.sku = d1.sku
  group by d1.classify,d.dt,d.warehouse_id ,d1.cur_sku
"""
sql2 = """
"""
sql3 = """
"""
sql4 = """
"""
sql_list = [sql1,sql2,sql3,sql4]

exec_sql_list = []
for item in sql_list:
    if 'select' in item.lower():
        exec_sql_list.append(item)

filename = f"D:\\数据导出_{DatePack.parseDatetime2Str(DatePack.getCurtime(),DatePack.YYYYMMDDHHMMSS)}.xlsx"

with pd.ExcelWriter(filename, engine='openpyxl') as writer:
    i = 1
    for sql in exec_sql_list:
        sheetname = f"sheet{i}"
        df = dbs.select(sql)
        df.to_excel(writer, sheet_name=sheetname, startcol=0, startrow=0, index=False, header=True)

print(f"导出文件名：{filename}")
os.startfile(filename)
