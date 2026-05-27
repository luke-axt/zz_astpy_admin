import sys
sys.path.append(r"D:\app\astpy")

from zzlc.script.MyAdmin import MyAdminBase
from utils .BrowserUtils import BrowserUtils



class xxxxxx(MyAdminBase):
    def __init__(self, jobname):
        super().__init__(jobname)
        self.jobname = jobname

    
    def action(self, **kwargs):
        browser = BrowserUtils.openChrome(chromdatapath=self.admin.getChromeUserPath(f'{self.__class__.__name__}.action'))
        pass

    def wait_confirm(self)-> bool:
        """
        等待用户输入：
        - 直接回车 = 继续
        - 输入 Y/y + 回车 = 继续
        - 其他输入 = 退出
        """
        user_input = input("请按回车确认，或输入 Y 继续：").strip().upper()
        
        # 空（直接回车）或者 Y 都通过
        if user_input == "" or user_input == "Y":
            print("✅ 确认通过，继续执行...")
            return True
        else:
            print("❌ 取消执行")
            return False
