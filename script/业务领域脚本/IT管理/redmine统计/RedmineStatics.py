import os

import pandas as pd

from utils.ExcelUtil import ExcelUtil
from 运维管理.MyAdmin import MyAdminBase

class RedmineProj(MyAdminBase):
    def __init__(self,jobname='Redmine统计'):
        super().__init__(jobname)
        self.proj_dict = {}
        self.init_proj_data()

    def init_proj_data(self):
        sql = """
SELECT id, name, parent_id
FROM redmine.projects
        """
        df = self.dbs.select(sql)
        for index,row in df.iterrows():
            self.proj_dict[row['id']] = row.to_dict()
            self.proj_dict[row['id']]['parent_id'] = None if pd.isna(self.proj_dict[row['id']]['parent_id']) else int(self.proj_dict[row['id']]['parent_id'])

        for k,v in self.proj_dict.items():
            path = self._get_ancestors(k,[])
            if len(path) < 5:
                path += [None]*(5-len(path))
            self.proj_dict[k]['path'] = path

    def get_proj_name(self,proj_id):
        if proj_id is None:
            return None
        return self.proj_dict.get(proj_id).get('name')

    def get_proj_parent_name(self,proj_id,p_level:int):
        """
        获取第p_level级的父节点的名称
        :param pid:
        :param p_level:  《= 4  0代表最高级的父节点
        :return:
        """
        if p_level > 4 or p_level <0:
            raise RuntimeError(F"p_level越界")
        pid = self.proj_dict.get(proj_id).get('path')[p_level]
        return self.get_proj_name(pid)

    def _get_ancestors(self,current_id, path: list):
        """递归收集从当前节点到根节点的路径"""
        if current_id not in self.proj_dict:
            return path  # 节点不存在，返回当前路径

        node = self.proj_dict[current_id]
        parent_id = node.get("parent_id")  # 空字符串视为 None

        # 如果没有父节点，说明是根或末端，当前节点加入路径并返回
        if parent_id is None:
            return [current_id] + path

        # 继续向上递归
        return self._get_ancestors(parent_id, [current_id] + path)


class RedmineStatics(MyAdminBase):

    def __init__(self,jobname='Redmine统计'):
        super().__init__(jobname)
        self.proj_obj = RedmineProj()


    def get_close_issue_info(self,start_dt,end_dt):
        sql = f"""
SELECT t1.child_name as proj_name
     , t.id as issue_id
     , t.project_id
     , t.subject
     , t.closed_on
     , t1.level1_name as L1_proj_name
     , t1.level2_name as L2_proj_name
     , t1.level3_name as L3_proj_name
  FROM redmine.issues t 
  left join redmine.v_proj_map t1
    on t.project_id = t1.child_id 
 where t.closed_on between '{start_dt} 00:00:00' and '{end_dt} 23:59:59'
        """
        df = self.dbs.select(sql)
        filename_tag = f"redmine已完成任务导出_{start_dt}_{end_dt}"
        filename = ExcelUtil.df_to_excel(df,filename_tag)
        os.startfile(filename)

start_dt = '2025-07-01'
end_dt = '2025-09-30'
RedmineStatics().get_close_issue_info(start_dt,end_dt)