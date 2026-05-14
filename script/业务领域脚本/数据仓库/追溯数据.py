import traceback

from dwd.DwService import DwService
from utils.dateutil import DatePack

dt = '2025-08-30'
stop_dt = '2025-01-01'
while dt >= stop_dt:
    paramJson = f"""[{{"format":"{{order_dt}}","value":"{dt}"}}]"""
    try:
        res = DwService('dml').run_job('dml_sale_order_info', paramJson)
        print(f"{dt} - {res}")
    except:
        print(f"{dt} - {traceback.format_exc()}")
        exit(1)

    dt = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.parseStr2Datetime(dt,DatePack.YYYY_MM_DD),-1),DatePack.YYYY_MM_DD)
