from ETL.ods.OrangeConnexOdsJob import OrangeConnexOdsJob
from task.JobCore import JobCore

res = JobCore().run_job(jobid=243,start_date='2026-01-25',end_date='2026-03-10')  # 临时

print(f"{res}")


# print(OrangeConnexOdsJob('橙联出库订单采集').queryOutboundOrderInfo(start_time='2025-09-15',end_time='2025-09-29'))



