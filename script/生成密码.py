import os
import sys

sys.path.append(r"D:\app\astpy")
from zzlc.script.LCService import LCService

astadmin = LCService()

for i in range(1,14):
    print(f'{astadmin.genPasswd()}')
# print(f'生成的appsecret：  {astadmin.genAstAppsecret()}')
