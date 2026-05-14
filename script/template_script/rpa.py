import sys
sys.path.append(r"D:\app\astpy")
from CoreBussiness.LingXingService import LingXingService
from common.ResultObj import ResultObj
from rpa.RpaAdmin import RpaAdmin
from admin.service.AdminService import AdminService
from utils .BrowserUtils import BrowserUtils



class xxxxxx(RpaAdmin):
    def __init__(self, jobname):
        super().__init__(jobname)
        self.jobname = jobname

    
    def action(self, **kwargs):
        browser = BrowserUtils.openChrome(chromdatapath=self.admin.getChromeUserPath(f'{self.__class__.__name__}.action'))
        pass
