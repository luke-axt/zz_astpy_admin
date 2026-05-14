import json

from CoreBussiness.AstdcService import AstdcAPI
from admin.service.AdminService import AdminService
from common.ResultObj import ResultObj
from utils.ExcelUtil import ExcelUtil
from utils.dateutil import DatePack
from 运维管理.MyAdmin import MyAdminBase

class MyQywxService:

    def __init__(self):
        self.admin = AdminService()
        self.appid = self.admin.get_config()['astapi']['appid']
        self.appsecret = self.admin.get_config()['astapi']['appsecret']
        self.astdcService = AstdcAPI()
        self.qywx_add_token="BFj9jQo4t4OV1Ni8bNWXxRNLfDi"

    def api_get_dept_list(self):
        action = 'https://qyapi.weixin.qq.com/cgi-bin/department/list'
        json_param = {'id': 1}
        res = self.astdcService.call_qywx_serv_api(action=action,qywx_add_token=self.qywx_add_token,json_param=json_param)
        return res

    def api_get_user_list(self,department_id:str):
        action = "https://qyapi.weixin.qq.com/cgi-bin/user/simplelist"
        json_param = {'department_id': department_id}
        res = self.astdcService.call_qywx_serv_api(action=action, qywx_add_token=self.qywx_add_token,
                                                   url_param=json_param)
        return res

    def api_sent_msg_to_user(self,msg,userid='ZhengCiLin'):
        action = "https://qyapi.weixin.qq.com/cgi-bin/message/send"
        if userid == 'ZhengCiLin':
            to_user_list = f"ZhengCiLin"
        else:
            to_user_list = f"ZhengCiLin|{userid}"
        json_param = {
                      "touser": to_user_list,
                      "msgtype": "text",
                      "agentid": 1000022,
                      "text": {
                        "content": msg
                      },
                      "safe": 0,
                      "enable_id_trans": 0,
                      "enable_duplicate_check": 0
        }
        res = self.astdcService.call_qywx_serv_api(action=action, qywx_add_token=self.qywx_add_token,
                                                   json_param=json_param)
        return res


# print(MyQywxService().api_get_dept_list())


class QywxImportData(MyAdminBase):

    def __init__(self,jobname):
        super().__init__(jobname)
        self.qywx = MyQywxService()

    def import_qywx_userid_list(self):
        res = self.qywx.api_get_dept_list()
        if res.is_fail():
            return res
        api_res = json.loads(res.get_data())
        if api_res['errcode'] != 0:
            return ResultObj.error(ResultObj.FATAL_ERROR,res.get_data())
        dept_data = api_res['department']
        data_list = []
        for dept_info in dept_data:
            if dept_info['parentid'] == 0:
                continue
            res = self.qywx.api_get_user_list(str(dept_info['id']))
            if res.is_fail():
                return res
            api_res = json.loads(res.get_data())
            if api_res['errcode'] != 0:
                return ResultObj.error(ResultObj.FATAL_ERROR, res.get_data())
            for item in api_res['userlist']:
                t_dict = item.copy()
                t_dict['department'] = str(t_dict['department'])
                t_dict['datasyntime'] = DatePack.getCurtime()
                data_list.append(t_dict)

        rows = self.dbs.insertmysql('replace','astdc.qywx_user_info',data_list)
        self.logger.info(f'更新{rows}行数据。')
        return ResultObj.success()

    def get_qwuserid_by_ryusername(self,username):
        sql = """
select t1.qywx_id 
  from astdc.qywx_user_map t1
  join astdc.sys_user t2
    on t1.ry_id = t2.user_id 
 where t2.user_name = %s
        """
        df = self.dbs.select(sql,(username,))
        if len(df) == 0:
            raise RuntimeError(f"{username} 缺少映射关系。")
        if len(df) != 1:
            raise RuntimeError(f"{username} 存在一对多的映射关系。")
        return df['qywx_id'].iloc[0]
    def notice_lx_user_info(self):
        """
        一次性方法，通知领星用户初始密码
        :return:
        """
        res = ExcelUtil.read_excel_file(r"\\192.168.1.62\郑词林\文档\工作目录\20250616-通途切换领星\供应链用户创建\领星初始化密码.xlsx")
        data_passwd = res.get_data()
        for index,row in data_passwd.iterrows():
            qw_userid = self.get_qwuserid_by_ryusername(row['用户名'])
            passwd = row['初始密码']
            msg =f"""
已分配领星账号如下：
登录地址：https://auxito.lingxing.com/erp/home
用户名：{row['用户名']}
初始密码：{passwd}

请先登录系统修改初始密码，已初步分配使用权限，后续使用遇到问题再按需调整。            
"""
            self.qywx.api_sent_msg_to_user(qw_userid,msg)

        a = 1


