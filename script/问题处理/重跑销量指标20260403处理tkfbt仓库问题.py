import time

from zzlc.script.业务领域脚本.数据仓库.跑数处理类 import RunDataHis

time.sleep(60*20)
start_dt = '20260501'
stop_dt = '20260521'

RunDataHis().run_sale_idx(start_dt=start_dt, stop_dt=stop_dt)
