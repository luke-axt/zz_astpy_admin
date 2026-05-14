import json

import bcrypt
import requests

from admin.service.DBcore import DBcore
from admin.service.adminconfig import AdminConfig
from utils.StringUtils import StringUtils
import random

from zzlc.MyAdmin import MyAdminBase


class User:
    def __init__(self, cnname, phone, email,dept_id):
        self.cnname = cnname
        self.phone = phone
        self.email = email
        self.user_id = None
        self.passwd = None
        self.user_code = None
        self.set_user_code()
        self.dept_id = dept_id
        if self.email is None:
            self.email = (self.user_code if self.user_code is not None else '') + '@sztyqcypyxgs.wecom.work'

    def get_dept_id(self):
        return self.dept_id

    def set_user_code(self):
        pinyinname = StringUtils.parse_hanzi_to_pinyin(self.cnname)
        self.user_code = pinyinname
        for i in range(0,3):
            j = random.randint(0, 9)
            self.user_code += str(j)
        return

    def get_passwd(self):
        return self.passwd

    def set_passwd(self, passwd):
        self.passwd = passwd

    def get_user_id(self):
        return self.user_id

    def set_user_id(self, user_id):
        self.user_id = user_id

    def get_user_code(self):
        return self.user_code
    def get_cnname(self):
        return self.cnname

    def set_cnname(self, cnname):
        self.cnname = cnname

    def get_phone(self):
        return self.phone

    def set_phone(self, phone):
        self.phone = phone

    def get_email(self):
        return self.email

    def set_email(self, email):
        self.email = email



class UserCore(MyAdminBase):

    def __init__(self,cnname='', phone='', email='',deptname=''):
        super().__init__('用户管理')
        self.mapper = UserMapper()
        self.cnname = cnname
        self.phone = phone
        self.email = email
        self.deptid = self.get_dept_id(deptname)
        self.user_id = None

    def test(self):
        sql = """
update tmp.t_zcl_2col set c1 = 'aa' where id = 1;
update tmp.t_zcl_2col set c1 = 'bb' where id = 2;
        """
        self.dbs.exec_many_sql_new(sql)

    def get_dept_id(self,dept_name):
        df = self.mapper.get_dept_id(dept_name)
        if len(df) == 0:
            print(f"{dept_name} 查不到该部门名称。请输入一级部门：产品、运营、供应链、IT、人力")
            return 0
        else:
            return df['dept_id'][0]

    def get_user_id(self,user_code):
        df = self.mapper.select_user(user_code)
        if len(df) == 0:
            raise RuntimeError("查询用户信息失败。前置步骤插入新用户失败。")

        return df['user_id'][0]

    def is_cnname_exists(self):
        """
        检查用户的中文名是否存在
        """
        sql = "select count(*) as cnt from astdc.sys_user t where t.nick_name = %s"
        return self.dbs.select(sql,(self.cnname,))['cnt'][0] > 0

    def modify_user_passwd(self,usercode):
        """
        为用户生成新密码
        """
        passwd = StringUtils.gen_random_str(10)
        sql = """
UPDATE astdc.sys_user
SET password=%s, update_by='admin', update_time=now(), remark='修改密码'
WHERE user_name=%s;
        """
        res = self.dbs.update(sql, (self.encrypt_password(passwd),usercode))
        if res == 1:
            msg = f"""更新{usercode} 成功！
系统登录地址：http://192.168.1.60/login?redirect=/index
用户编号：{usercode}
用户密码：{passwd}
"""
            print(msg)
        else:
            print(f"""更新{usercode} 失败。{res}！""")

    def create_ry_user(self):
        if self.is_cnname_exists():
            print(f"{self.cnname} 已经存在，此用户创建失败，请检查。")
            return
        user = User(self.cnname, self.phone, self.email,self.deptid)
        user_password = StringUtils.gen_random_str(10)
        user.set_passwd(self.encrypt_password(user_password))
        user.set_email(user.get_user_code() + '@no.com' if user.get_email() is None or '@no.com' in user.get_email() else user.get_email())
        self.mapper.insert_ry_user(user)
        user.set_user_id(self.get_user_id(user.get_user_code()))
        self.mapper.insert_ry_common_role(user)


        # newPassword = self.updatePasswdByUname(user)  # 取消自动修改密码的方法
        # print(f"需人工修改用户密码：{newPassword}")
        print(
            f"""
{user.get_cnname()} 用户创建成功！
系统登录地址：http://192.168.1.60/login?redirect=/index
用户编号：{user.get_user_code()}
用户密码：{user_password}
"""
        )

    def encrypt_password(self, password: str, strength: int = 10) -> str:
        """
        与java一样的加密逻辑，用此方法加密，java一样可以验证
        """
        if password is None or len(password)<6:
            raise ValueError("rawPassword cannot be null or less then 6 letters")

        # 编码为字节
        password_bytes = password.encode('utf-8')

        # 生成 salt，指定 rounds=strength（即 cost）
        # 注意：bcrypt.gensalt(rounds) 中 rounds 范围是 4~31
        salt = bcrypt.gensalt(rounds=strength)

        # 哈希密码
        hashed = bcrypt.hashpw(password_bytes, salt)

        # 返回字符串（格式如 $2b$10$...）
        return hashed.decode('utf-8')

    def astAuth(self):
        api_url = "http://192.168.1.60:8080/test/user/login"
        headers = {
            "Content-Type": "application/json",
            "accept": "*/*"
        }
        param = {
            "username": 'zhengcilin791',
            "password": 'U8.Ytr53'
        }
        response = requests.post(api_url, json=param, headers=headers)
        jsondata = json.loads(response.text)
        if jsondata["code"] == 200:
            return jsondata["token"]
        else:
            raise RuntimeError(f"登录使用到 zhengcilin 这个用户，密码不正确。" + response.text)

    def updatePasswdByUname(self, user:User):

        token = self.astAuth()
        token = "Bearer " + token
        # API 的 URL

        headers = {
            "Content-Type": "application/json",
            "Authorization": token,
            "accept": "*/*"
        }
        # 要传递的参数
        newPassword = StringUtils.gen_random_str(8)
        api_url = "http://192.168.1.60:8080/system/user/profile/updatePwd22?userName=" + user.get_user_code() + "&newPassword=" + newPassword
        # 发送 POST 请求
        response = requests.put(api_url, headers=headers)
        jsondata = json.loads(response.text)
        if jsondata["code"] == 200:
            # print("用户：" + user_code + " 修改密码成功！新密码： " + newPassword)
            return newPassword
        else:
            raise RuntimeError(response.text)

class UserMapper(MyAdminBase):
    def __init__(self):
        super().__init__('用户管理数据操作')

    def insert_ry_user(self, user:User):
        sql = f"""
INSERT INTO astdc.sys_user (dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, create_by, create_time, update_by, update_time, remark)
VALUES( {user.get_dept_id()}, '{user.get_user_code()}',    '{user.get_cnname()}', '00', '{user.get_email()}',  '{user.get_phone()}', '', '', '{user.get_passwd()}', '0', '0', '127.0.0.1', sysdate(), 'admin', sysdate(), '', null, '');
        """
        return self.dbs.insert(sql)

    def insert_ry_common_role(self,user:User):
        sql = f"insert into astdc.sys_user_role values(%s,  100)"
        return self.dbs.insert(sql,(user.get_user_id()))

    def get_dept_id(self,dept_name):
        sql = f"""
        SELECT dept_id, parent_id, ancestors, dept_name, order_num, leader, phone, email, status, del_flag, create_by, create_time, update_by, update_time
FROM astdc.sys_dept
where  dept_name = %s
        """
        return self.dbs.select(sql,(dept_name,))

    def select_user(self,user_code):
        sql = f"""
        SELECT user_id, dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, create_by, create_time, update_by, update_time, remark
FROM astdc.sys_user
where user_name = %s
        """
        return self.dbs.select(sql,(user_code,))
