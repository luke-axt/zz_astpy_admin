# parse_html_table.py
from html.parser import HTMLParser
import re


class TableParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tables = []
        self.current_table = []
        self.current_row = []
        self.in_td = False
        self.in_tr = False

    def handle_starttag(self, tag, attrs):
        if tag == 'tr':
            self.in_tr = True
            self.current_row = []
        elif tag == 'td':
            self.in_td = True

    def handle_endtag(self, tag):
        if tag == 'tr':
            if self.current_row:
                self.current_table.append(self.current_row)
            self.in_tr = False
        elif tag == 'td':
            self.in_td = False

    def handle_data(self, data):
        if self.in_td:
            # 清理空白字符，保留有意义的文本
            clean_data = re.sub(r'\s+', ' ', data).strip()
            self.current_row.append(clean_data)

    def get_tables_as_list_of_dicts(self):
        result = []
        for table in [self.current_table]:  # 只处理主表（可扩展多表）
            if not table:
                continue
            # 动态生成列名：col_0, col_1, col_2, ...
            max_cols = max(len(row) for row in table)
            for row in table:
                # 补齐缺失列（防止 IndexError）
                padded_row = (row + [''] * max_cols)[:max_cols]
                row_dict = {f'col_{i}': val for i, val in enumerate(padded_row)}
                result.append(row_dict)
        return result


def parse_html_table_from_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        html_content = f.read()

    parser = TableParser()
    parser.feed(html_content)
    return parser.get_tables_as_list_of_dicts()


# 示例使用
if __name__ == "__main__":
    # 假设你的 HTML 片段保存在 D:\tbodytr.txt
    input_file = r"C:\Users\luke\Documents\Untitled-2.html"

    try:
        data = parse_html_table_from_file(input_file)
        print("解析结果（前3行）：")
        for i, row in enumerate(data[:3]):
            print(f"Row {i}: {row}")

        # 如果你想只取 col_0 和 col_2（即系统单号和错误信息）
        simplified = [
            {
                "系统单号": row["col_0"],
                "col_218文本": row["col_2"]
            }
            for row in data
            if row["col_0"].isdigit() and row["col_0"].startswith("103")
        ]

        print("\n简化后（仅103开头的纯数字单号）：")
        for item in simplified:
            print(item)

    except Exception as e:
        print(f"解析出错: {e}")
