from dwd.DwService import DwService

dt = '2026-03-14'
paramJson = f"""[{{"format":"{{dt}}","value":"{dt}"}}]"""

res = DwService('dml').run_job('dml_sale_salevol', paramJson)
print(res)