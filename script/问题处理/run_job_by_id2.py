from ETL.ods.OrangeConnexOdsJob import OrangeConnexOdsJob
from task.JobCore import JobCore

# res = JobCore().run_job(jobid=64)  # dml_idx_sale
# res = JobCore().run_job(jobid=79)  # 	adl计划sku信息
# res = JobCore().run_job(jobid=122)  # sku监控
# res = JobCore().run_job(jobid=13)  # 采集通途产品信息rpa
# res = JobCore().run_job(jobid=3,startdate='2024-07-01',enddate='2024-07-02')
# res = JobCore().run_job(jobid=5,start_dt='2024-06-07',end_dt='2024-06-10')
# res = JobCore().run_job(jobid=70)               #  tt_product_info
# res = JobCore().run_job(jobid=111)               #   odl_tt_product_info
# res = JobCore().run_job(jobid=83)               #  TaskDwdDml:TaskDML.job_dml_inv_inbound_info
# res = JobCore().run_job(jobid=62)               #  dml_inv_prod_storage
# res = JobCore().run_job(jobid=65) # dml_prod_info
# res = JobCore().run_job(jobid=87,dt='20241205') # dml_idx_inv_plan_base
# res = JobCore().run_job(jobid=88)   # dml_idx_inv_plan
# res = JobCore().run_job(jobid=134)  # dml_prod_status_not_amz
# res = JobCore().run_job(jobid=90,dt='20250117')  # 采购需求表 bal_plan_purchase_new
# print(f"{res}")
# res = JobCore().run_job(jobid=90,dt='20250118')  # 采购需求表 bal_plan_purchase_new
# print(f"{res}")
# res = JobCore().run_job(jobid=90,dt='20250419')  # 采购需求表 bal_plan_purchase_new
# res = JobCore().run_job(jobid=141)  # 年货采购详情
# res = JobCore().run_job(jobid=142)  # 年货采购及催货结果
# res = JobCore().run_job(jobid=149)
# res = JobCore().run_job(jobid=108)  # 采集领星listing数据
# res = JobCore().run_job(jobid=134)  # TaskDwdDml:TaskDML.job_dml_prod_status_not_amz
# res = JobCore().run_job(jobid=180)  # TaskDwdDml:TaskDML.job_dml_sku_3rd_stock_status
# res = JobCore().run_job(jobid=216)  # TaskLX:TaskLX.import_lx_erp_user_info  领星采集erp用户
# res = JobCore().run_job(jobid=214)  # 采集领星本地库存 TaskLX:TaskLX.import_lx_inv_local_inventory

# res = JobCore().run_job(jobid=218)  # TaskXbb.import_xbb_contract_info
# print(f"{res}")
# res = JobCore().run_job(jobid=212,dt='20250909')  # bal头程固化综合报价_终版
# res = JobCore().run_job(jobid=222)  # 同步xbb订单到领星
# res = JobCore().run_job(jobid=217)  # 销帮帮采集产品信息
# res = JobCore().run_job(jobid=228, hour_cal=13)  # 领星多平台订单小时批
# res = JobCore().run_job(jobid=164)  # 同步xbb订单到领星
# res = JobCore().run_job(jobid=228)  # 多平台订单
res = JobCore().run_job(jobid=270)  # 临时
# res = JobCore().run_job(jobid=243,start_date='2026-01-25',end_date='2026-03-10')

print(f"{res}")


# print(OrangeConnexOdsJob('橙联出库订单采集').queryOutboundOrderInfo(start_time='2025-09-15',end_time='2025-09-29'))



