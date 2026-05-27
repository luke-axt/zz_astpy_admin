from ETL.ods.OrangeConnexOdsJob import OrangeConnexOdsJob
from task.JobCore import JobCore
from utils.dateutil import DatePack

start_dt = '20260423'
stop_dt = '20260423'
dt = start_dt
while dt <= stop_dt:

    res = JobCore().run_job(jobid=232,dt=dt,count_day=3) # TaskDwdBal:TaskBAL.job_bal_ebay_susporder_info
    print(f"{dt} - {res}")
    if res.is_fail():
        break
    res = JobCore().run_job(jobid=233,dt=dt)   # TaskDwdAdl:TaskADL.task_get_ebay_suspect_order
    print(f"{dt} - {res}")
    if res.is_fail():
        break
    dt = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.parseStr2Datetime(dt, DatePack.YYYYMMDD), 1),
                                    DatePack.YYYYMMDD)

print(f"全部结束")




