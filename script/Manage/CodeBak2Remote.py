from ETL.SmbService import SmbService
from common.ResultObj import ResultObj
from utils.dateutil import DatePack
from 运维管理.MyAdmin import MyAdminBase
import os
import zipfile
from pathlib import Path



class CodeBak2Remote(MyAdminBase):


    def __init__(self,jobname):
        super().__init__(jobname)

    def action(self,**kwargs):
        code_list = [
            {'code_dir': r'D:\app\astpy', 'zipfile_tag': 'python_astpy'},
            {'code_dir': r'D:\code\java\AST', 'zipfile_tag': 'java_AST'},
            {'code_dir': r'D:\code\deploy', 'zipfile_tag': 'deploy'},
                    ]
        error_msg = ''
        for item in code_list:
            res = self.zip_codefile_and_push(item['code_dir'], item['zipfile_tag'])
            if res.is_fail():
                error_msg += res.get_msg()

        if error_msg == '':
            return ResultObj.success()
        else:
            return ResultObj.error(ResultObj.FATAL_ERROR, error_msg)


    def gzip_code_file_in_dir(self,source_dir, output_zip) -> ResultObj:
        """
        遍历目录，将所有 .py .sql .bat .xml 文件打包成 zip
        :param source_dir: 要遍历的根目录
        :param output_zip: 输出的 zip 文件路径
        """
        source_path = Path(source_dir)
        if not source_path.exists():
            return ResultObj.error(ResultObj.FATAL_ERROR,f"目录不存在: {source_dir}")

        with zipfile.ZipFile(output_zip, 'w', zipfile.ZIP_DEFLATED) as zipf:
            count = 0
            for file_path in source_path.rglob('*'):
                if file_path.is_file() and file_path.suffix.lower() in ['.py', '.bat', '.sql', '.xml', '.java']:
                    # 保存相对路径到压缩包
                    arcname = file_path.relative_to(source_path)
                    zipf.write(file_path, arcname)
                    print(f"已添加: {arcname}")
                    count += 1

        self.logger.info(f"打包完成！共 {count} 个文件，保存为: {output_zip}")
        return ResultObj.success()

    def zip_codefile_and_push(self,code_dir, zipfile_tag):
        """
        自动备份数据，并删除90天前的备份文件，每月1号的文件不删除
        :param code_dir: 要遍历的根目录
        :param zipfile_tag: 压缩文件的文件名的前缀
        :return:
        """
        curdate = DatePack.parseDatetime2Str(DatePack.getCurtime(),DatePack.YYYYMMDD)
        last90date = DatePack.parseDatetime2Str(DatePack.addDays(DatePack.getCurtime(), -60), DatePack.YYYYMMDD)
        smb62 = SmbService(self.smb62_info)
        remote_dir = r"\\192.168.1.62\郑词林\代码备份"
        zipfile_local = rf"D:\tmp\{zipfile_tag}_{curdate}.zip"
        if os.path.exists(r"D:\tmp") is False:
            os.makedirs(r"D:\tmp")
        zipfile_old_remote = rf"{remote_dir}\{zipfile_tag}_{last90date}.zip"

        res = self.gzip_code_file_in_dir(code_dir, zipfile_local)
        if res.is_fail():
            self.logger.error(res.get_msg())
            return res

        smb62.copyfileLocal2Remote(zipfile_local,remote_dir)

        if last90date[6:8] != '01':
            if os.path.exists(zipfile_old_remote):
                smb62.remove_remoteFile(zipfile_old_remote)

        return ResultObj.success()

