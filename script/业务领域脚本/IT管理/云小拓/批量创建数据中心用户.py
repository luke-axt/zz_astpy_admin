import sys
sys.path.insert(0, r"D:\app\astpy")

from zzlc.script.UserCore import UserCore

"""
此脚本实现创建用户及分配小拓桌面权限
"""


"""
role_name_astcli
供应链-计划公共权限,供应链-采购-公共角色,供应链-仓库公共角色,供应链-总监角色,供应链-计划主管角色,供应链-物流尾程角色,供应链-采购-采购主管
财务公共权限,财务_报销角色,财务-经理角色,
系统维护权限,开发测试角色,
运营-ebay公共角色,运营-SWOT经理角色,运营-独立站经理角色,运营-ebay组长角色,运营-ebay经理角色,运营-amz经理角色,
产品-ebay产品角色,
郑词林测试,全权,

-- 输入数据示例
user_name = '陶小苏'
dept_name_yxt = 'ebay'  # 必填，云小拓部门名称：IT;财务;ebay;亚马逊;SWOT;独立站;采购;计划;设计部;外贸;物流;仓库;质检;人事行政部;
role_name_astcli = ''        # 选填，小拓桌面角色，空值或空字符串则不分配;  
"""
# email 为None的话，会生成一个 user_code@sztyqcypyxgs.wecom.work 的邮箱

u_list = [
    {'user_name':'陶小苏','dept_name_yxt':'ebay','role_name_astcli':'运营-ebay公共角色'},
    # {'user_name':'xxx','dept_name_yxt':'ebay','role_name_astcli':'运营-ebay公共角色'},
]
user_core = UserCore()
for item in u_list:
    user_core.create_user_and_assign_role(user_name=item['user_name'],dept_name_yxt=item['dept_name_yxt'],role_name_astcli=item['role_name_astcli'])

#  历史版本2 2026-7-22 ------------------------------------
# u_str_list = """
# 陶小苏|ebay|17777777777|17777777777@no.com
# """
# userlist = []
# for item in u_str_list.split('\n'):
#     if item == '':
#         continue
#     info_tuple = item.split('|')
#     if len(info_tuple) != 4:
#         raise RuntimeError(f"格式错误，解析后长度不为4")

#     user_name = info_tuple[0]
#     dept_name = info_tuple[1]
#     phone = '11111111111' if info_tuple[2] is None or info_tuple[2] == '' else info_tuple[2]
#     email = 'no@ast.com' if info_tuple[3] is None or info_tuple[3] == '' else info_tuple[3]
#     # userlist.append((user_name,phone,email,dept_name))
#     userlist.append({'user_name':user_name,'phone':phone,'email':email,'dept_name':dept_name})

# for item in userlist:
#     user_core = UserCore(item['user_name'],item['phone'],item['email'],item['dept_name'])
#     user_core.create_ry_user()

#  历史版本1 ------------------------------------

# email = 'ast@ast.com'
# userlist = []
# userlist.append(("植慧敏",'15989463440',email,'SWOT'))
# userlist.append(("杨毓",'18688886666','yangyu@auxito.com','财务'))
# userlist.append(("谢晓丽",'18688886666','oukeke@sztyqcypyxgs.wecom.work','供应链'))

# userlist.append(("测试",'18688886666',email,'独立站'))
# userlist.append(("测试",'18688886666',email,'ebay'))
# userlist.append(("测试",'18688886666',email,'亚马逊'))
# userlist.append(("测试",'18688886666',email,'IT'))
# userlist.append(("测试",'18688886666',email,'SWOT'))
# userlist.append(("测试",'18688886666',email,'产品'))
# userlist.append(("测试",'18688886666',email,'采购'))
# userlist.append(("测试",'18688886666',email,'计划'))
# userlist.append(("测试",'18688886666',email,'设计部'))



