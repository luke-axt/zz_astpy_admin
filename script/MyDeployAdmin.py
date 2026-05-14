import os

from utils.LogUtils import LogUtils
from utils.WinSysUtils import WinSysUtils
from utils.dateutil import DatePack

projectPath = r'D:\code\javaproject\AST'

class DeployUtil:

    def __init__(self):
        pass
    @staticmethod
    def delete_old_bak_jar():
        """
        最多保留5个备份的jar文件，多余的自动删除。
        :return:
        """

        # jarPath = os.path.join(projectPath,r"D:\code\javaproject\AST\ruoyi-admin\target"
        jarPath = os.path.join(projectPath,r"ruoyi-admin\target")
        file_list = os.listdir(jarPath)
        bakfileList = []
        for filename in file_list:
            jarfile = os.path.join(jarPath, filename)
            if 'ast.jar.bak' in filename and os.path.isfile(jarfile):
                bakfileList.append(jarfile)

        if len(bakfileList) < 6:
            return

        LogUtils.print(f"最多保留5个备份jar文件，多余的删除。")
        sortedKeyList = sorted(bakfileList)
        delNum = len(sortedKeyList) - 5
        i = 0
        while i<delNum:
            file2Del = sortedKeyList[i]
            LogUtils.print(f"删除旧的备份jar文件：  {file2Del}")
            os.remove(file2Del)
            i += 1

    @staticmethod
    def deploy_jar():
        """
        部署jar包到60服务器
        本地备份jar包
        :return:
        """
        dt = DatePack.parseDatetime2Str(DatePack.getCurtime(), DatePack.YYYYMMDDHHMMSS)
        # localJarfile = r"D:\code\javaproject\AST\ruoyi-admin\target\ast.jar"
        localJarfile = os.path.join(projectPath,r"ruoyi-admin\target\ast.jar")
        localBakfile = f"{localJarfile}.bak{dt}"
        remotePath = r'appusr@192.168.1.60:/app/datacenter'
        bak_command = f"copy {localJarfile} {localBakfile}"
        deploy_command = f"scp {localJarfile} {remotePath}"

        LogUtils.print("本地备份jar包.....")
        WinSysUtils.runWindowsCmd(bak_command)

        LogUtils.print("部署jar包.....")
        WinSysUtils.runWindowsCmd(deploy_command)

        # 删除多余的jar包
        DeployUtil.delete_old_bak_jar()

        LogUtils.print("若提示命令执行成功，则可前往服务器，执行命令重启服务：  sh /app/datacenter/restart.sh   ")

    @staticmethod
    def deploy_sql(days):
        """
        根据输入的天数部署sql文件到192.168.1.60服务器。输入1，代表上传最近一天又变更的sql文件。以此类推...
        :param days:
        :return:
        """

        LogUtils.print(DeployUtil.deploy_sql.__doc__)
        # localPath = r"D:\code\javaproject\AST\rpt\rptsql"
        localPath = os.path.join(projectPath,r"rpt\rptsql")
        print(localPath)
        remotePath = r'appusr@192.168.1.60:/app/datacenter/uploadPath/rptsql'

        # 获取目录中的文件列表
        file_list = os.listdir(localPath)
        deployList = []

        # 遍历文件列表并获取更新时间
        for filename in file_list:
            localSqlfile = os.path.join(localPath, filename)
            if os.path.isfile(localSqlfile):  # 确保是文件而不是子目录
                file_stat = os.stat(localSqlfile)
                file_update_time = DatePack.parseTimestamp2Date(file_stat.st_mtime)
                if file_update_time >  DatePack.addDays(DatePack.getCurtime(), 0-days):
                    deploy_command = f"scp {localSqlfile} {remotePath}"
                    LogUtils.print(f"部署sql文件: {filename}")
                    LogUtils.print(f"部署命令: {deploy_command}")
                    WinSysUtils.runWindowsCmd(deploy_command)
                    deployList.append(filename)

        if len(deployList) == 0:
            LogUtils.print(f"sql文件未更新，无需部署。")

    @staticmethod
    def deploy_all():
        DeployUtil.deploy_jar()
        DeployUtil.deploy_sql(-2)

    @staticmethod
    def deploy_dist():
        LogUtils.print("部署前端包.....")
        deploy_command = r'scp -r D:\code\javaproject\AST\web\dist appusr@192.168.1.60:/app/datacenter'
        WinSysUtils.runWindowsCmd(deploy_command)

    @staticmethod
    def deploy_python(local_path=r'D:\app\astpy',server_path=r'D:\app\astpy'):
        server_ip_list = ['192.168.1.63','192.168.1.65','192.168.1.67']
        dir_list = ['admin','client','common','CoreBussiness','dwd','ETL','rpa','rpt','statics','task','utils','辅助工具']
        for server_ip in server_ip_list:
            for dir in dir_list:
                deploy_command = rf'scp -r {os.path.join(local_path,dir)} usr_ssh@{server_ip}:{os.path.join(server_path,dir)}'
                print(f"运行命令： {deploy_command}")
                WinSysUtils.runWindowsCmd(deploy_command)






