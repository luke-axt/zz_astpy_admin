import sys
sys.path.append(r"D:\app\astpy")



from 运维管理.业务领域脚本.企业微信.MyQywxService import MyQywxService, QywxImportData
from ETL.ods.ToogtoolOds.TtPurchaseOrder import ImportTtPurchaseOrder
from 运维管理.MyAdmin import MyAdminBase
from rpa.common.RefreshAmzPrivAstdcJob import RefreshAmzPrivAstdcJob

class TestUnit(MyAdminBase):

    def __init__(self,jobname='IT视图授权'):
        super().__init__(jobname)
    

    def action(self):
        self.email.sendmailnew('lc_3030@163.com','test','test')

    def send_passcode(self):
        tstr = """liuxiaowei845：w6Bxx31Et
liuziyan301：t4Tj2yBFI
humin410：i2B8IuSiY
zhuyin397：z9Z9D4Kv1
yangrong580：v2RzNVQsk
fengyiqi580：g5P1f16ZM
shenkaiman618：q9SPwRBbd
wangchunli191：v7BRb4CjY
wuzhixin848：a8M9V1iW5
chenzhilin603：i2Te3XVa2
zhuqiang515：v7E98vmZ6
majinfeng757：q9V851UE7
cengxinyan525：t5Y4ky14k
caihaini484：e9SD18tXy
liliting241：e1Q6jY24i
zhouyaonan853：j5ELn988X
qiutingting766：j5Lu9u9Dz
linqian328：v4S9jFSMW
kangjie112：r5XEE779n
yangzhiyuan849：j7Wei6Z67
lintong442：s6PkeZ9au
dengliping660：r9ZUSS9t2
xiejiewen809：v5Xb54W88
mahaohao273：r2AY5g9cY
xiaqinghong266：x6Twc16x5"""

        qywx = MyQywxService()
        for item in tstr.split('\n'):
            ucode,pcode = item.split('：')
            msg = f"""
用户创建成功！
系统登录地址：http://192.168.1.60/login?redirect=/index
用户编号：{ucode}
用户密码：{pcode}

此站点可以查询库存数据，不过权限还没开放好，等开好了建雪通知你们。
使用指南：http://192.168.1.68/redmine/projects/itdeploy0073/wiki/001SKU%E8%A7%86%E5%9B%BE
"""

            sql = f"""
select d.user_code as qywxusercode
  from astdc.sys_user s
  join astdc.dc_user_map d
    on s.user_id = d.ry_user_id 
   and d.user_type = 'qywx'
 where s.user_name ='{ucode}'
"""
            qywxusercode = self.dbs.select(sql)['qywxusercode'][0]
            qywx.api_sent_msg_to_user(msg=msg,userid=qywxusercode)
            pass
            



# TestUnit('test').run()
print(RefreshAmzPrivAstdcJob('test').run())
# QywxImportData('test').import_qywx_userid_list()
# TestUnit('test').send_passcode()