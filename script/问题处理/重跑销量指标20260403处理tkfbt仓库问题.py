
from 运维管理.业务领域脚本.数据仓库.跑数处理类 import RunDataHis

start_dt = '20260324'
stop_dt = '20260401'

RunDataHis().run_sale_idx(start_dt=start_dt, stop_dt=stop_dt)
