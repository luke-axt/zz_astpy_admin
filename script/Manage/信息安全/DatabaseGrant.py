import traceback

from common.ResultObj import ResultObj
from zzlc.script.MyAdmin import MyAdminBase


class DBPrivGrant(MyAdminBase):

    def __init__(self,jobname='IT视图授权'):
        super().__init__(jobname)
        self.set_userdefine_ddl()

    def check(self,full_tablename) -> ResultObj:
        if '.' not in full_tablename:
            res = ResultObj.error(ResultObj.INVALID_INPUT, f'输入不正确，输入表名格式：table_schema.table_name，输入：{full_tablename}')
            self.logger.error(res.get_msg())
            return res
        return ResultObj.success()


    def create_it_view(self,full_tablename) -> ResultObj:
        """
        创建it视图
        :param tablename: ast.bal_sale_ddxx
        :return:
        """
        full_tablename = full_tablename.replace('`','')
        res = self.check(full_tablename)
        if res.is_fail():
            return res
        
        table_schema = full_tablename.split('.')[0]
        table_name = full_tablename.split('.')[1]
        
        sqltext = self.get_it_view_ddl(table_schema,table_name)
        try:
            self.dbs.exec_many_sql(sqltext)
            self.logger.info(f"{full_tablename} 创建it视图成功。")
        except:
            self.logger.error(f"{full_tablename} 失败：{traceback.format_exc()}")

        return ResultObj.success()

    def get_it_view_ddl(self,table_schema:str,table_name:str) -> str:
        """

        :param tablename:
        :return:
        """
        col_df = self.get_col_info(table_schema,table_name)
        if len(col_df) == 0:
            res = ResultObj.error(ResultObj.INVALID_INPUT, f'输入不正确，查询不到表的字段信息，输入：{table_schema}.{table_name}')
            self.logger.error(res.get_msg())
            return res
        
        # 如果有自定义sql，直接使用
        sqltext = self.get_userdefine_ddl(table_schema,table_name)
        if sqltext is not None:
            return sqltext

        view_name = f"it.`{table_schema}_{table_name}`"
        sqltext = f"""
drop view if exists {view_name}; 
create view {view_name} as select 
"""

        for index,row in col_df.iterrows():
            ordinal_position = row['ORDINAL_POSITION']
            safe_col_value = row['COLUMN_NAME'] if row['sql_rule'] is None else row['sql_rule']
            if ordinal_position == 1:
                sqltext += f" {safe_col_value} \n"
            else:
                sqltext += f",{safe_col_value} \n"

        sqltext += f"  from {table_schema}.`{table_name}` \n;"
        return sqltext


    def set_userdefine_ddl(self):
        t_self_ddl = {
            'ast.amz_lrbb_n': """
drop view if exists it.ast_amz_lrbb_n; 
create view it.ast_amz_lrbb_n as  
SELECT `基础信息-日期`, `基础信息-MSKU`, `基础信息-ASIN`, `基础信息-父ASIN`, `基础信息-店铺`, `基础信息-国家`, `基础信息-品名`, `基础信息-SKU`, `基础信息-标题`, `基础信息-Listing负责人`, `领星导出-Listing负责人`, `基础信息-开发负责人`, `基础信息-分类`, `基础信息-品牌`, `基础信息-币种`, `基础信息-Listing标签`
FROM ast.amz_lrbb_n;
            """
        }
        # 将key转换为小写
        self.userdefine_ddl_dict = {}
        for key, value in t_self_ddl.items():
            self.userdefine_ddl_dict[key.lower()] = value

    def get_userdefine_ddl(self,table_schema:str,table_name):
        safe_key = f"{table_schema.lower()}.{table_name.lower()}"
        return self.userdefine_ddl_dict.get(safe_key)

    def get_col_info(self,table_schema,table_name):
        sql = """
SELECT c1.ORDINAL_POSITION ,c1.COLUMN_NAME,c2.sql_rule 
  FROM INFORMATION_SCHEMA.columns c1 
  left join meta_store.it_view_rule c2 
    on lower(c1.table_schema) = lower(c2.schema_name)
   and lower(c1.TABLE_NAME) = lower(c2.table_name) 
   and lower(c1.column_name) = lower(c2.col_name) 
 where c1.table_schema = %s and c1.TABLE_NAME = %s
 order by c1.ORDINAL_POSITION
        """
        return self.dbs.select(sql,(table_schema,table_name))



