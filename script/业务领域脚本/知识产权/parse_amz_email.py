import html
import re
from datetime import datetime
from email import message_from_binary_file
from email.utils import parsedate_to_datetime
from pathlib import Path

import pandas as pd


class ParseAmzEmail:
    """
    邮件目录：D:\data\autoone\品牌投诉邮件导出
    需求细化：
    1. 直接在此文件实现，不新建脚本。
    2. 递归解析目录下所有 .eml 格式邮件。
    3. 提取发件日期（Date header）、邮件主题（Subject）、邮件文件绝对路径、
       邮件正文中的 ASIN（正则 \bB[A-Z0-9]{9,10}\b，不区分大小写）。
    4. 一个 ASIN 占一行；同一邮件多个 ASIN 则展开为多行，日期/主题/路径相同。
    5. 若邮件解析失败（编码异常、格式损坏、无法提取正文等），仍记录一行，
       ASIN 列填写"解析失败"。
    6. 整理好的数据导出到 Excel：D:\data\autoone\数据整理yyyymmddhhmm.xlsx
    """

    ASIN_PATTERN = re.compile(r'\bB[A-Z0-9]{9,10}\b', re.IGNORECASE)

    def __init__(
        self,
        source_dir: str = r'D:\data\autoone\品牌投诉邮件导出',
        output_dir: str = r'D:\data\autoone',
    ):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)

    def run(self) -> None:
        eml_files = list(self.source_dir.rglob('*.eml'))
        rows = []
        for eml_path in eml_files:
            rows.extend(self._parse_email(eml_path))

        df = pd.DataFrame(
            rows,
            columns=['发件日期', '邮件主题', '邮件文件绝对路径', 'ASIN'],
        )
        timestamp = datetime.now().strftime('%Y%m%d%H%M')
        output_path = self.output_dir / f'数据整理{timestamp}.xlsx'
        self.output_dir.mkdir(parents=True, exist_ok=True)
        df.to_excel(output_path, index=False)
        print(f'已导出：{output_path}')

    def _parse_email(self, path: Path) -> list[dict]:
        try:
            with open(path, 'rb') as f:
                msg = message_from_binary_file(f)
        except Exception:
            return [
                {
                    '发件日期': '',
                    '邮件主题': '',
                    '邮件文件绝对路径': str(path),
                    'ASIN': '解析失败',
                }
            ]

        date_str = msg.get('Date', '')
        try:
            dt = parsedate_to_datetime(date_str)
            date_str = dt.strftime('%Y-%m-%d %H:%M')
        except Exception:
            pass  # 保留原始字符串

        subject_str = msg.get('Subject', '')

        body = self._extract_body(msg)
        if body is None:
            return [
                {
                    '发件日期': date_str,
                    '邮件主题': subject_str,
                    '邮件文件绝对路径': str(path),
                    'ASIN': '解析失败',
                }
            ]

        asins = list(set(self.ASIN_PATTERN.findall(body)))
        if not asins:
            return [
                {
                    '发件日期': date_str,
                    '邮件主题': subject_str,
                    '邮件文件绝对路径': str(path),
                    'ASIN': '解析失败',
                }
            ]

        return [
            {
                '发件日期': date_str,
                '邮件主题': subject_str,
                '邮件文件绝对路径': str(path),
                'ASIN': asin.upper(),
            }
            for asin in asins
        ]

    def _extract_body(self, msg) -> str | None:
        try:
            if msg.is_multipart():
                for part in msg.walk():
                    content_type = part.get_content_type()
                    if content_type == 'text/plain':
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        return payload.decode(charset, errors='ignore')
                    elif content_type == 'text/html':
                        payload = part.get_payload(decode=True)
                        charset = part.get_content_charset() or 'utf-8'
                        html_text = payload.decode(charset, errors='ignore')
                        return self._strip_html(html_text)
            else:
                content_type = msg.get_content_type()
                if content_type == 'text/plain':
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    return payload.decode(charset, errors='ignore')
                elif content_type == 'text/html':
                    payload = msg.get_payload(decode=True)
                    charset = msg.get_content_charset() or 'utf-8'
                    html_text = payload.decode(charset, errors='ignore')
                    return self._strip_html(html_text)
            return None
        except Exception:
            return None

    @staticmethod
    def _strip_html(html_text: str) -> str:
        text = re.sub(r'<[^>]+>', '', html_text)
        text = html.unescape(text)
        return text


if __name__ == '__main__':
    ParseAmzEmail().run()
