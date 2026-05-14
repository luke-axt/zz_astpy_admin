import bcrypt

from ETL.ods.LingxingOdsJob import LingxingOdsJob

# def encrypt_password(password: str, strength: int = 10) -> str:
#     if password is None:
#         raise ValueError("rawPassword cannot be null")
#
#     # 编码为字节
#     password_bytes = password.encode('utf-8')
#
#     # 生成 salt，指定 rounds=strength（即 cost）
#     # 注意：bcrypt.gensalt(rounds) 中 rounds 范围是 4~31
#     salt = bcrypt.gensalt(rounds=strength)
#
#     # 哈希密码
#     hashed = bcrypt.hashpw(password_bytes, salt)
#
#     # 返回字符串（格式如 $2b$10$...）
#     return hashed.decode('utf-8')
#


print(LingxingOdsJob('测试').import_lx_shipmentList())