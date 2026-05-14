import sys

sys.path.append(r"D:\app\astpy")
from admin.service.AdminService import AdminService
from utils.EncryptUtils import EncryptUtils


admin = AdminService()
input = 'QEQPqtrJydbswBd7'
pass1 = EncryptUtils.encryptFernet(input, admin.get_config()['yaoshi'])
print(f'加密前字符串：{input}')
print(f'加密后字符串：{pass1}')


input = 'gAAAAABpwz7MUvkULRhYU6598ZrX-dOD2FRmlOBBr95tz-nAPJKtvRlYhFHV5x76dC5mbXacilOaPzwCCfB0pt69_oYsevSgI70iQz6sZrh0c8WBp-FI7FQ='
print(f'解密后的值：{admin.decryptFernet(input)}')