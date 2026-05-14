import pandas as pd
import os
from datetime import datetime
from 运维管理.MyAdmin import MyAdminBase

class ProblemDeal(MyAdminBase):
    def __init__(self,jobname='问题处理'):
        super().__init__(jobname)


    def update_redmine_from_excel(self):
        """
        读取 Excel，生成 SQL 更新 MySQL，并将结果回写到新 Excel 文件中。
        """
        # 1. 配置路径和参数
        source_file = r"C:\Users\luke\Documents\通途切换方案-IT.xlsx"
        sheet_name = "全量功能清单"

        # 生成新文件名：在原文件名后加上时间戳，避免覆盖
        file_dir = os.path.dirname(source_file)
        file_name = os.path.basename(source_file)
        name, ext = os.path.splitext(file_name)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        target_file = os.path.join(file_dir, f"{name}_更新后_{timestamp}{ext}")

        # 2. 读取 Excel 数据
        # dtype={'redmine问题id': str} 确保读取时不自动转换数字格式，方便后续判断
        try:
            df = pd.read_excel(source_file, sheet_name=sheet_name, dtype={'redmine问题id': str})
        except Exception as e:
            raise Exception(f"读取 Excel 失败: {str(e)}")

        # 定义需要提取的字段列表 (用于构建 desc_add_str)
        # 注意：这里必须与 Excel 中的列名完全一致
        columns_to_extract = [
            '组件', '功能名称', '负责人', '评审状态', '进度状态', '评审结论',
            '切换方案', '切换备注', '数据使用情况', '统一功能id', '影响范围',
            '功能技术类型', '原始id', '上1级名称', '上2级名称', '备注2'
        ]

        # 3. 逐行处理逻辑
        print(f"开始处理，共 {len(df)} 行数据...")

        for index, row in df.iterrows():
            redmine_id_val = row.get('redmine问题id')
            status = row.get('修改redmine状态')
            if pd.isna(status) is False and status == '成功':
                continue

            # 逻辑判断：只有当【redmine问题id】是纯数字时才处理
            # 处理可能的空白或非字符串情况
            if redmine_id_val is None or not isinstance(redmine_id_val, str):
                continue

            clean_id = redmine_id_val.strip()
            if not clean_id.isdigit():
                # 不是数字，跳过，不回写任何内容
                continue

            if int(clean_id) not in (979,980,981):
                continue

            # 是数字，准备执行更新
            try:
                # 构建描述字符串 desc_add_str
                # # 使用 get 防止列名缺失导致报错，缺失则显示为空
                # desc_parts = []
                # for col in columns_to_extract:
                #     val = row.get(col, "")
                #     # 处理 NaN 值，转为空字符串
                #     if pd.isna(val):
                #         val = ""
                #     desc_parts.append(f"{col}：{val}")

                # 按照您提供的格式拼接，注意开头和结尾的换行
                # desc_add_str = "xaxaxa\n以下是 excel 文档内容\n---\n" + "\n---\n".join(desc_parts) + "\n---\n备注2"
                # 修正：根据您提供的模板，最后一项是"备注2"，上面的 join 逻辑可能需要微调以完全匹配模板
                # 重新严格按照模板构建：
                desc_add_str = f"""xaxaxa
以下是 excel 文档内容

---

评审结论：{row.get('评审结论', '') if not pd.isna(row.get('评审结论', '')) else ''}

---

组件：{row.get('组件', '') if not pd.isna(row.get('组件', '')) else ''}

---

功能名称：{row.get('功能名称', '') if not pd.isna(row.get('功能名称', '')) else ''}

---

负责人：{row.get('负责人', '') if not pd.isna(row.get('负责人', '')) else ''}

---

评审状态：{row.get('评审状态', '') if not pd.isna(row.get('评审状态', '')) else ''}

---

进度状态：{row.get('进度状态', '') if not pd.isna(row.get('进度状态', '')) else ''}

---

切换方案：
{row.get('切换方案', '') if not pd.isna(row.get('切换方案', '')) else ''}

---

切换备注：
{row.get('切换备注', '') if not pd.isna(row.get('切换备注', '')) else ''}

---

数据使用情况：
{row.get('数据使用情况', '') if not pd.isna(row.get('数据使用情况', '')) else ''}

---

统一功能 id：{row.get('统一功能 id', '') if not pd.isna(row.get('统一功能 id', '')) else ''}

---

影响范围：
{row.get('影响范围', '') if not pd.isna(row.get('影响范围', '')) else ''}

---

功能技术类型：{row.get('功能技术类型', '') if not pd.isna(row.get('功能技术类型', '')) else ''}

---

原始 id：{row.get('原始 id', '') if not pd.isna(row.get('原始 id', '')) else ''}

---

上 1 级名称：{row.get('上 1 级名称', '') if not pd.isna(row.get('上 1 级名称', '')) else ''}

---

上 2 级名称：{row.get('上 2 级名称', '') if not pd.isna(row.get('上 2 级名称', '')) else ''}

---

备注2：
{row.get('备注 2', '') if not pd.isna(row.get('备注 2', '')) else ''}
"""

                # 构造 SQL 和参数
                sql = """
                UPDATE redmine.issues
                SET description = CONCAT(description, %s)
                WHERE id = %s;
                """
                params = (desc_add_str, int(clean_id))

                # 调用您提供的更新方法
                # 假设 self.dbs.update 返回受影响的行数，或者不返回但出错会抛异常
                # 如果 update 方法没有返回值代表成功，这里假设不抛异常即成功
                self.dbs.update(sql, params)

                # 更新成功：标记为 "成功"
                df.at[index, '修改redmine状态'] = "成功"

            except Exception as e:
                # 更新失败：记录错误原因
                error_msg = f"更新失败：{str(e)}"
                df.at[index, '修改redmine状态'] = error_msg
                print(f"ID {clean_id} 更新失败: {error_msg}")

        # 4. 保存为新文件 (保留原格式)
        # 使用 openpyxl 加载原文件进行复制，以确保公式、格式、列宽等不被破坏
        try:
            df.to_excel(target_file,index=False)
            print(f"处理完成！新文件已保存至: {target_file}")
        except Exception as e:
            raise Exception(f"保存 Excel 文件失败: {str(e)}")


# 使用示例 (在您已有的类实例中调用)
updater = ProblemDeal()
updater.update_redmine_from_excel()
