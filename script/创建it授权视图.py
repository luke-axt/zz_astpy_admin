import os
import sys

sys.path.append(r"D:\app\astpy")
import traceback

table_list_str = """
astdc.qywx_user_info
astdc.qywx_user_map
"""
from zzlc.script.Manage.信息安全.DatabaseGrant import DBPrivGrant

dbg = DBPrivGrant()

table_list = table_list_str.split('\n')
for table_name in table_list:
    if len(table_name) == 0:
        continue
    if len(table_name) < 4:
        dbg.logger.error(f"{table_name} 表名过短，跳过。")
        continue
    try:
        dbg.create_it_view(table_name)
    except:
        dbg.logger.error(f"{table_name} 报错；{traceback.format_exc()}")
        exit(1)
