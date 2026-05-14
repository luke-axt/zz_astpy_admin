import os

import pandas as pd

from admin.service.EmailService import EmailService
from utils.ExcelUtil import ExcelUtil
from 运维管理.MyAdmin import MyAdminBase

class ProblemDeal(MyAdminBase):
    def __init__(self,jobname='问题处理'):
        super().__init__(jobname)



email = EmailService()
email.sendmailnew('lc_3030@163.com','test1233212222','test')

