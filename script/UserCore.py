
import traceback
import bcrypt
from utils.StringUtils import StringUtils
import random
from zzlc.script.MyAdmin import MyAdminBase

class UserCore(MyAdminBase):
    """
    创建用户及分配角色
    """

    def __init__(self):
        super().__init__('用户管理')

    def create_user_and_assign_role(self,user_name,dept_name_yxt,role_name_astcli=None):
        try:
            self.create_ry_user_action(user_name,dept_name_yxt,role_name_astcli)
            self.logger.info(f"用户名：{user_name} 创建用户及权限分配运行结束")
        except:
            self.logger.error(f"用户名：{user_name} 创建用户及权限分配失败。{traceback.format_exc()}")
            return 

    def create_ry_user_action(self,user_name,dept_name_yxt,role_name_astcli=None):
        """
        创建云小拓用户，启用小拓桌面用户，分配小拓桌面角色
        
        :param user_name: Description
        :param dept_name_yxt: Description
        :param role_name_astcli: Description
        """
        self.logger.info(f"开始运行用户创建及权限分配：user_name：{user_name}，dept_name_yxt：{dept_name_yxt}，role_name_astcli：{role_name_astcli}")
        # 检查部门名称是否正确
        dept_id = self.check_dept_name(dept_name_yxt)
        # 检查角色名称是否正确
        role_id = self.check_role_name_astcli(role_name_astcli)
        # 检查是否存在重名
        qw_user_code,yxt_user_id = self.check_username(user_name)
        # 如果尚未创建云小拓用户，则创建
        if yxt_user_id is None:
            yxt_user_id, user_code = self.create_ry_user2(user_name,dept_id,qw_user_code)
        # 启用小拓桌面账户及分配角色
        self.valid_user_xt_desktop(user_name,yxt_user_id,qw_user_code,role_id)


    def check_role_name_astcli(self,role_name_astcli):
        """
        Docstring for check_role_name_astcli
        
        :param self: Description
        :param role_name_astcli: Description
        """
        if role_name_astcli is None:
            return None
        df = self.dbs.select("select role_id from astdc.cli_role where role_name = %s",(role_name_astcli,))
        if len(df) != 1:
            raise RuntimeError(f"role_name_astcli： {role_name_astcli} 查询角色名称异常，请检查。查询数量：{len(df)}")
        return df['role_id'][0]
        
    def valid_user_xt_desktop(self,user_name,yxt_user_id,qw_user_code,role_id):
        """
        Docstring for valid_user_xt_desktop
        
        :param self: Description
        :param user_name: Description
        :param yxt_user_id: Description
        :param role_id: Description
        """
        df = self.dbs.select("select cli_user_id,status,ry_user_id from astdc.cli_user t where t.cn_name = %s",(user_name,))
        if len(df) == 0:
            self.qywx.send_app_msg(f'你好，正在给你开通小拓桌面权限。检测到你尚未初始化导致无法开通。请先安装小拓桌面，然后使用自己的中文名登录，完成这个动作之后联系郑词林继续开通权限。安装包地址：\\\\192.168.1.80\\工具软件\\办公软件\\小拓桌面\\install.exe',qw_user_code)
            raise RuntimeError(f"用户名：{user_name} 未初始化小拓桌面，无法授权")
        if len(df) > 1:
            raise RuntimeError(f"用户名：{user_name} 小拓桌面存在多个同名用户，请先清理后再继续")
        if df['ry_user_id'][0] is None or df['status'][0] is None or df['status'][0] == 'N':
            affect_rows = self.dbs.update("update astdc.cli_user t set t.ry_user_id = %s, t.status = 'Y' where t.cli_user_id = %s;",(yxt_user_id, df['cli_user_id'][0]))
            self.logger.info(f"用户名：{user_name} 启用用户成功 affect_rows:{affect_rows}")
        else:
            self.logger.info(f"用户名：{user_name} 用户已启用，本次未处理。")
        
        if role_id is not None:
            df = self.dbs.select("select role_id from astdc.cli_user_role t where t.user_id = %s and t.role_id = %s ",(yxt_user_id,role_id))
            if len(df) == 0:
                self.dbs.insert("INSERT INTO astdc.cli_user_role (user_id, role_id) values (%s,%s)",(yxt_user_id,role_id))
                self.logger.info(f"用户名：{user_name} 分配角色成功")
                self.qywx.send_app_msg(f'{user_name}， 你好，小拓桌面权限开通成功。',qw_user_code)
            
            else:
                self.logger.info(f"用户名：{user_name} 已分配角色，本次未处理。")


    def check_username(self,user_name):
        """
        检查企微是否重名
        检查云小拓是否已经创建用户
        返回，is_qw_ok,qw_user_code,yxt_user_id,is_yxt_ok
        
        :param self: Description
        :param user_name: Description
        """
        qw_user_code = None
        yxt_user_id = None
        keyword = f"%{user_name}"
        df = self.dbs.select("select q.userid as qw_user_code from astdc.qywx_user_info q where q.name like %s",(keyword,))
        if len(df) == 0:
            raise RuntimeError(f"用户名：{user_name}，企微用户表不存在此用户，请检查或者重新采集企微用户表（作业id：286）")
        if len(df) > 1:
            raise RuntimeError(f"用户名：{user_name}，在企微表重名，请检查，如确实重名，只能人工处理。")
        qw_user_code = df['qw_user_code'][0]
        df = self.dbs.select("select q.user_id  from astdc.sys_user q where q.nick_name = %s",(user_name,))
        if len(df) > 1:
            raise RuntimeError(f"用户名：{user_name}，云小拓已存在2个以上的用户，请检查")
        if len(df) == 1:
            yxt_user_id = df['user_id'][0]
        return qw_user_code,yxt_user_id
    
    def check_dept_name(self,dept_name):
        """
        检查部门名称，成功返回部门id
        
        :param self: Description
        :param dept_name: Description
        """
        df = self.dbs.select("select dept_id from astdc.sys_dept where dept_name = %s",(dept_name,))
        if len(df) != 1:
            raise RuntimeError(f"dept_name： {dept_name} 查不到该部门名称，请检查")
        return df['dept_id'][0]
    
    def generate_user_code(self,user_name):
        pinyinname = StringUtils.parse_hanzi_to_pinyin(user_name)
        for i in range(0,3):
            j = random.randint(0, 9)
            pinyinname += str(j)
        return pinyinname
    

    def create_ry_user2(self,user_name,dept_id,qw_user_code):
        """
        创建云小拓用户，返回用户id和用户编号，自动配置企微用户映射
        
        :param self: Description
        :param user_name: Description
        :param dept_id: Description
        :param qw_user_code: Description
        """
        
        user_password = StringUtils.gen_random_str(10)
        print(user_password)
        user_password_encrypt = self.encrypt_password(user_password)
        user_code = self.generate_user_code(user_name)
        sql = f"""
INSERT INTO astdc.sys_user (dept_id, user_name, nick_name, user_type, email, phonenumber, sex, avatar, password, status, del_flag, login_ip, login_date, create_by, create_time, update_by, update_time, remark)
VALUES( {dept_id}, '{user_code}',   '{user_name}', '00', '',  '', '', '', '{user_password_encrypt}', '0', '0', '127.0.0.1', sysdate(), 'admin', sysdate(), '', null, '');
        """
        self.dbs.insert(sql)
        self.logger.info(f"创建云小拓用户。")
        print(
            f"""
{user_name} 用户创建成功！
云小拓系统登录地址：http://192.168.1.60/login?redirect=/index
领星系统登录地址：https://auxito.lingxing.com/login   # 需要单独开通权限，如需要，找主管申请。
用户编号：{user_code}
用户密码：{user_password}
"""
        )

        user_id_ry = self.get_user_id(user_code)
        self.dbs.insert(f"insert into astdc.sys_user_role values(%s,  100)",(user_id_ry,))
        self.logger.info(f"分配云小拓基础权限。")

        self.dbs.insert(f"INSERT INTO astdc.dc_user_map (user_type, user_code, ry_user_id, ry_user_name) VALUES('qywx', %s, %s, %s);",(qw_user_code,user_id_ry,user_name))
        self.logger.info(f"插入企微云小拓用户映射。")
        return user_id_ry, user_code

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

