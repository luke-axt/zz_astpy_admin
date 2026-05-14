from ETL.SmbService import SmbService
from admin.service.AdminService import AdminService
from utils.EncryptUtils import EncryptUtils

admin = AdminService()

user_dict = {
    'server': '192.168.1.62',
    'username': 'zengyan858',
    'password': EncryptUtils.encryptFernet('mUdc2Q3c', admin.get_config()['yaoshi']),
}

localfile=r'D:\test.txt'
remote_directory=r'\\192.168.1.62\通途主图'
# SmbService(admin.get_config()['qhnas']).copyfileLocal2Remote(localfile, remote_directory)
SmbService(user_dict).copyfileLocal2Remote(localfile, remote_directory)

