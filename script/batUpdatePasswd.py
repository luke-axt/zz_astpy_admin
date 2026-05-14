from 辅助工具.LCService import LCService

userlist = []
# userlist.append("zhengcilin791")
# userlist.append("liugaoxiong")

astadmin = LCService()
for item in userlist:
    astadmin.updatePasswdByUname(item)
