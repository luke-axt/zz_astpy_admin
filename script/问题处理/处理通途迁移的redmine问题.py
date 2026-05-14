
import pandas as pd

from 运维管理.MyAdmin import MyAdminBase

class ProblemDeal(MyAdminBase):
    def __init__(self,jobname='问题处理'):
        super().__init__(jobname)


    def _proc_my(self):
        # 读取Excel文件
        file_path = r"C:\Users\luke\Documents\通途切换方案-IT.xlsx"
        sheet_name = "全量功能清单"

        # 读取数据（跳过标题行以外的内容，但保留第一行为列名）
        df = pd.read_excel(file_path, sheet_name=sheet_name, header=0)

        # 确保列名正确（处理可能的空格或换行）
        df.columns = df.columns.str.strip()

        # 定义目标字段（按你提供的顺序）
        required_columns = [
            "redmine问题id", "是否完成", "切换方案", "数据使用情况", "切换备注",
            "统一功能id", "备注1", "影响范围", "组件", "备注2"
        ]

        # 检查所有字段是否存在
        missing_cols = [col for col in required_columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少列: {missing_cols}")

        for idx, row in df.iterrows():
            redmine_id = row["redmine问题id"]

            # 只处理 redmine问题id 是数字的情况（包括整数、浮点数如 123.0）
            if pd.isna(redmine_id):
                continue
            try:
                # 尝试转换为整数（兼容 123.0 这样的浮点）
                redmine_id_int = int(float(redmine_id))
            except (ValueError, TypeError):
                continue  # 不是数字，跳过


            # 提取其他字段，将 NaN 或 None 转为空字符串
            def clean(val):
                return "" if pd.isna(val) else str(val).strip()


            data = {
                "是否完成": clean(row["是否完成"]),
                "切换方案": clean(row["切换方案"]),
                "数据使用情况": clean(row["数据使用情况"]),
                "切换备注": clean(row["切换备注"]),
                "统一功能id": clean(row["统一功能id"]),
                "备注1": clean(row["备注1"]),
                "影响范围": clean(row["影响范围"]),
                "组件": clean(row["组件"]),
                "备注2": clean(row["备注2"]),
            }

            # 构造 desc_add_str
            desc_add_str = f"""
xaxaxa
---
是否完成：{data['是否完成']}
---
切换方案：{data['切换方案']}
---
数据使用情况：{data['数据使用情况']}
---
切换备注：{data['切换备注']}
---
统一功能id：{data['统一功能id']}
---
备注1：{data['备注1']}
---
影响范围：{data['影响范围']}
---
组件：{data['组件']}
---
备注2：{data['备注2']}
        """

            # 生成SQL（注意：desc_add_str 中可能含单引号，需转义）
            escaped_desc = desc_add_str.replace("'", "''")  # SQL 单引号转义
            sql = f"UPDATE redmine.issues SET description = CONCAT(description, %s) WHERE id = %s;"
            affr = self.dbs.update(sql,(escaped_desc, row["redmine问题id"]))
            if affr == 1:
                self.logger.info(f"{row['redmine问题id']},")
            pass


ProblemDeal()._proc_my()

