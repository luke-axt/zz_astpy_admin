import os
import base64
from Crypto.Cipher import DES
from Crypto.Hash import MD5
from Crypto.Protocol.KDF import PBKDF1
from Crypto.Util.Padding import pad, unpad


def jasypt_pbe_encrypt(plain_text: str, password: str, salt: bytes = None) -> str:
    """
    复刻 Java Jasypt PBEWithMD5AndDES 加密：
    - Algorithm: PBEWithMD5AndDES
    - IvGenerator: NoIvGenerator（IV 由 PBKDF1 派生，无需外部 IV）
    - SaltGenerator: RandomSaltGenerator（默认 8 字节随机 salt）
    - Iterations: 1000
    - Output: Base64(salt[8B] + ciphertext)

    若传入固定 salt，则可得到与 Java 完全一致的输出（需 Java 端使用相同 salt）。
    """
    iterations = 1000
    dk_len = 16  # PBKDF1 输出 16 字节：前 8 字节为 Key，后 8 字节为 IV

    # 1. 生成或接收 8 字节 salt
    if salt is None:
        salt = os.urandom(8)
    elif len(salt) != 8:
        raise ValueError("salt must be exactly 8 bytes")

    # 2. PBKDF1 派生 Key + IV（与 Java JCE PBEWithMD5AndDES 一致）
    key_iv = PBKDF1(password.encode("utf-8"), salt, dk_len, iterations, MD5)
    key = key_iv[:8]
    iv = key_iv[8:16]

    # 3. DES-CBC 加密（PKCS7 填充）
    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    padded_data = pad(plain_text.encode("utf-8"), DES.block_size)
    encrypted = cipher.encrypt(padded_data)

    # 4. salt 附加在密文前，再 Base64 编码（Jasypt 标准格式）
    return base64.b64encode(salt + encrypted).decode("utf-8")


def jasypt_pbe_decrypt(encrypted_b64: str, password: str) -> str:
    """
    解密 Jasypt PBEWithMD5AndDES 格式的密文。
    """
    iterations = 1000
    dk_len = 16
    raw_cipher = encrypted_b64.strip()
    if raw_cipher.startswith("ENC(") and raw_cipher.endswith(")"):
        raw_cipher = raw_cipher[4:-1]
    raw = base64.b64decode(raw_cipher)
    if len(raw) < 8:
        raise ValueError("invalid encrypted data")

    salt = raw[:8]
    ciphertext = raw[8:]

    key_iv = PBKDF1(password.encode("utf-8"), salt, dk_len, iterations, MD5)
    key = key_iv[:8]
    iv = key_iv[8:16]

    cipher = DES.new(key, DES.MODE_CBC, iv=iv)
    padded_plain = cipher.decrypt(ciphertext)
    return unpad(padded_plain, DES.block_size).decode("utf-8")


if __name__ == "__main__":
    # ========== 配置区域（对应 Java 代码）==========
    encrypt_password = "xxxxx"  
    DB_PASSWORD = "xxxxx"
    REDIS_PASSWORD = "xxx"
    qwbot_secret = "QEdToJfP4nYxxxxx9xjExxeEeh"
    jobapi_token = "jH0qzN5geNoYxxxxxxyRUz/2LcEXxxM="

    # ==========================================

    # 演示：正常随机 salt 加密（每次结果不同，但与 Java 互通）
    DB_PASSWORD_enc = jasypt_pbe_encrypt(DB_PASSWORD, encrypt_password)
    REDIS_PASSWORD_enc = jasypt_pbe_encrypt(REDIS_PASSWORD, encrypt_password)
    qwbot_enc = jasypt_pbe_encrypt(qwbot_secret, encrypt_password)
    jobapi_enc = jasypt_pbe_encrypt(jobapi_token, encrypt_password)

    # 演示：解密验证
    db_dec = jasypt_pbe_decrypt(DB_PASSWORD_enc, encrypt_password)
    redis_dec = jasypt_pbe_decrypt(REDIS_PASSWORD_enc, encrypt_password)
    qwbot_dec = jasypt_pbe_decrypt(qwbot_enc, encrypt_password)
    jobapi_dec = jasypt_pbe_decrypt(jobapi_enc, encrypt_password)

    print("========================================")
    print("Jasypt 加密结果（复制到 .env 文件）")
    print("========================================")
    print()
    print(f"DB_PASSWORD=ENC({DB_PASSWORD_enc})")
    print(f"REDIS_PASSWORD=ENC({REDIS_PASSWORD_enc})")
    print()
    print("========================================")
    print("Jasypt 加密结果（复制到数据库 astdc.dc_sys_config 表）")
    print("========================================")
    print()
    print(f"wecom.bot.secret.jasypt=ENC({qwbot_enc})")
    print(f"wecom.job.api.token.jasypt=ENC({jobapi_enc})")
    print()
    print()
    print("========================================")
    print("提示：")
    print("  - 因使用随机 salt，每次加密结果不同，属正常行为")
    print("  - 若需与 Java 某次输出逐字节相同，请使用固定 salt 调用")
    print("  - 示例: jasypt_pbe_encrypt('123456', password, salt=b'\\x01\\x02...')")
    print("========================================")




