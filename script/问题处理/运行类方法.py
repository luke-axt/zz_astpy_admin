import sys
sys.path.append(r"D:\app\astpy")
from ETL.ods.LingXingOds.ImportLxSzInvFlow import ImportLxSzInvFlow

kwargs={
    'start_date':'2026-01-01',
    'end_date':'2026-03-21',
}
print(ImportLxSzInvFlow('test').run(**kwargs))

