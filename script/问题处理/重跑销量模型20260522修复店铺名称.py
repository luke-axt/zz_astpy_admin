import time

from zzlc.script.业务领域脚本.数据仓库.跑数处理类 import RunDataHis


start_dt = '2026-04-23'
stop_dt = '2026-05-23'

jobname = '重跑DML销量模型'
RunDataHis().run_dml_sale(taskname=jobname, start_dt=start_dt, stop_dt=stop_dt)
# RunDataHis().run_dml_sale()
