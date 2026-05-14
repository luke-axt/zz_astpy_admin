import json
import os
import random

import requests
from pypinyin import pinyin, Style

from 运维管理.LCMapper import LCMapper
from utils.ConfigUtils import ConfigUtils


class LCService:
    def __init__(self):
        self.mapper = LCMapper()
        self.big = "ABCDEFGHIJKLMNPQRSTUVWXYZ";
        self.small = "abcdefghijklmnpqrstuvwxyz";
        self.num = "0123456789"

    def getUnameByHanzi(self, hanzi):
        pinyin_list = pinyin(hanzi, style=Style.NORMAL)
        pinyin_str = ''.join([item[0] for item in pinyin_list])
        return pinyin_str

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
            user = 'zhengcilin791'
            raise RuntimeError(f"登录使用到{user}这个用户，密码不正确。" + response.text)

    # 给用户名增加3个数字后缀
    def parseUsername(self, username):
        num = "0123456789"
        j = random.randint(0, 9)
        username = username + num[j]
        j = random.randint(0, 9)
        username = username + num[j]
        j = random.randint(0, 9)
        username = username + num[j]
        return username

    def createUserByCNname(self, cnname):
        pinyinname = self.getUnameByHanzi(cnname)
        username = self.parseUsername(pinyinname)
        userid = self.mapper.getNewUserid()
        self.mapper.createuser(userid, username, cnname)
        password = self.updatePasswdByUname(username)
        print(
            f"用户创建成功！\n用户中文名：{cnname} \n用户编号：{username} \n用户密码：{password}\n请使用用户编号和密码登录系统，首次登录系统请修改密码！\n系统登录地址：http://192.168.1.60/login?redirect=/index\n")

    def updatePasswdByUname(self, userName):

        token = self.astAuth()
        token = "Bearer " + token
        # API 的 URL

        headers = {
            "Content-Type": "application/json",
            "Authorization": token,
            "accept": "*/*"
        }
        # 要传递的参数
        newPassword = self.genPasswd()
        param = {
            "userName": userName,
            "newPassword": newPassword
        }
        api_url = "http://192.168.1.60:8080/system/user/profile/updatePwd22?userName=" + userName + "&newPassword=" + newPassword
        # 发送 POST 请求
        response = requests.put(api_url, headers=headers)
        jsondata = json.loads(response.text)
        if jsondata["code"] == 200:
            print("用户：" + userName + " 修改密码成功！新密码： " + newPassword)
            return newPassword
        else:
            raise RuntimeError(response.text)

    def genPasswd(self):
        return self.genString(8)

    def genAstAppsecret(self):
        return self.genString(32)

    def genSqlcode(self,newid):
        newidstr = f"00000{str(newid)}"[-5:]
        return f"{newidstr}_{self.genString(25)}"

    def genRptcode(self,newid):
        newidstr = f"00000{str(newid)}"[-5:]
        return f"{newidstr}_{self.genString(15)}"

    def genString(self,length):
        i = 0
        str = ''
        while i < length:
            i += 1
            j = random.randint(0, 30)
            if j < 10:
                str += self.small[random.randint(0, 24)]
            elif j < 20:
                str += self.num[random.randint(0, 9)]
            else:
                str += self.big[random.randint(0, 24)]

        return str

    def createNewRptInfo(self):
        newrptid = self.mapper.getMaxRptid()+1
        newrptcode = self.genRptcode(newrptid)

        self.mapper.insertNewRptInfo(newrptid,newrptcode)


    def insertNewSqlInfo(self):
        newsqlid = self.mapper.getMaxRptsqlid()+1
        newsqlcode = self.genSqlcode(newsqlid)
        self.mapper.insertNewSqlInfo(newsqlid,newsqlcode)

    def createAstapiUser(self,astapi_app_list):

        self.mapper.createAstapiUser(astapi_app_list)


