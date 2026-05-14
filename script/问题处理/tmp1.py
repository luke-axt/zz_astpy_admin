from dwd.DwService import DwService

# dt = '2026-03-14'
# paramJson = f"""[{{"format":"{{dt}}","value":"{dt}"}}]"""
#
# res = DwService('dml').run_job('dml_sale_salevol', paramJson)
# print(res)

dt = '2026-03-14'
paramJson = f"""[{{"format":"{{order_dt}}","value":"{dt}"}}]"""

res = DwService('dml').run_job('dml_sale_order_info', paramJson)
print(res)
