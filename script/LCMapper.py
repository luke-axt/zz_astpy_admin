from admin.service.DBcore import DBcore
from admin.service.adminconfig import AdminConfig

class LCMapper:
    def __init__(self):
        self.dbs = DBcore(AdminConfig.get_db_info())

    def getNewUserid(self):
        sql = "SELECT IFNULL(MAX(user_id), 0) + 1 as newid FROM sys_user"
        df = self.dbs.select(sql)
        print(df['newid'][0])
        return df['newid'][0]

    def createuser(self,userid, username, cnname):
        sql = f"""
        insert into sys_user values({userid},  100, '{username}',    '{cnname}', '00', 'ast@ast.com',  '18666666666', '', '', 'passwd', '0', '0', '127.0.0.1', sysdate(), 'admin', sysdate(), '', null, '')
        """
        self.dbs.insert(sql)
        print(f"用户id：{userid} ，新增用户成功！")

        sql = f"insert into sys_user_role values({userid},  100);"
        self.dbs.insert(sql)
        print(f"用户id：{userid} ，设置普通用户权限成功！")

    def getMaxRptsqlid(self):
        sql = f"select ifnull(max(id),0) as maxid from dc_rpt_sql_info"
        df = self.dbs.select(sql)
        return df['maxid'][0]

    def getMaxRptid(self):
        sql = f"select ifnull(max(id),0) as maxid from dc_rpt_info"
        df = self.dbs.select(sql)
        return df['maxid'][0]

    def insertNewRptInfo(self,newid,newrptcode):
        sql = f"insert into dc_rpt_info value({newid},'{newrptcode}','未启用','未启用','admin',now())"
        return self.dbs.insert(sql)

    def insertNewSqlInfo(self,newsqlid,newsqlcode):
        sql = f"insert into dc_rpt_sql_info value({newsqlid},'{newsqlcode}','未启用','admin',now())"
        return self.dbs.insert(sql)

    def createAstapiUser(self,astapi_app_list):
        tablename = 'sys_openapi'
        self.dbs.insertmysql('insert ignore',tablename,astapi_app_list)

