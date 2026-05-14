import sys
sys.path.insert(0, r"D:\app\astpy")

from zzlc.UserCore import UserCore

# email 为None的话，会生成一个 user_code@sztyqcypyxgs.wecom.work 的邮箱
# 部门名称：IT;财务;ebay;亚马逊;SWOT;独立站;采购;计划;设计部;外贸;物流;仓库;
u_str_list = """
王美美|外贸|17777777777|17777777777@no.com
"""
userlist = []
for item in u_str_list.split('\n'):
    if item == '':
        continue
    info_tuple = item.split('|')
    if len(info_tuple) != 4:
        raise RuntimeError(f"格式错误，解析后长度不为4")

    user_name = info_tuple[0]
    dept_name = info_tuple[1]
    phone = '11111111111' if info_tuple[2] is None or info_tuple[2] == '' else info_tuple[2]
    email = 'no@ast.com' if info_tuple[3] is None or info_tuple[3] == '' else info_tuple[3]
    # userlist.append((user_name,phone,email,dept_name))
    userlist.append({'user_name':user_name,'phone':phone,'email':email,'dept_name':dept_name})

for item in userlist:
    user_core = UserCore(item['user_name'],item['phone'],item['email'],item['dept_name'])
    user_core.create_ry_user()

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



