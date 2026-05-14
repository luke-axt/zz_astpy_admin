from 运维管理.LCService import LCService

astadmin = LCService()

for i in range(1,10):
    print(f'生成的密码：  {astadmin.genPasswd()}')
# print(f'生成的appsecret：  {astadmin.genAstAppsecret()}')
