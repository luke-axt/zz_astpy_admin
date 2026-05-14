import time
import traceback

from common.ResultObj import ResultObj
from dwd.DwService import DwService
from utils.dateutil import DatePack

dt = '20251028'
paramJson = f"""[{{"format":"{{dt}}","value":"{dt}"}}]"""
try:
    res = DwService('bal').run_job('bal_yy_firstleg_detail_1b1p', paramJson)
    print(f"{dt} - {res} - {DatePack.getCurtime()}")
except:
    print(f"{dt} - {traceback.format_exc()} - {DatePack.getCurtime()}")
    res = ResultObj.error(ResultObj.FATAL_ERROR,traceback.format_exc())

if res.is_fail():
    exit(1)



