import imaplib
import email
import re
import time
import traceback
from email.header import decode_header
import datetime
from email.utils import parsedate_to_datetime

from common.ResultObj import ResultObj
from utils.dateutil import DatePack
from 运维管理.MyAdmin import MyAdminBase


class GetAliMailContactOrder(MyAdminBase):

    def __init__(self,jobname):
        super().__init__(jobname)
        self.IMAP_SERVER = "imap.qiye.aliyun.com"
        self.IMAP_PORT = 993
        self.EMAIL = "support@auxito.com"
        self.PASSWORD = "gAAAAABor8I8XuQo1_L-aqMbMNuwdpisEj_5L-TGwQeFIdbruPWSrObFKOHwnbIvOT-WHJx6HHRuDzwSWfvjLW3FCziu3_WpeqU8hJde-r_RohNSVEAhLhA="  # 客户端授权码，不是登录密码

    def init_mail_conn_obj(self):
        """
        登录并返回邮箱链接对象
        :return:
        """
        # 连接 IMAP 服务器
        self.mail = imaplib.IMAP4_SSL(self.IMAP_SERVER, self.IMAP_PORT)
        self.mail.login(self.EMAIL, self.admin.decryptFernet(self.PASSWORD))

    def decode_mime_header(self,header):
        """
        解码邮件头，兼容 unknown-8bit 等非标准编码
        """
        if header is None:
            return ""

        try:
            decoded_list = decode_header(header)
            fragments = []
            for fragment, encoding in decoded_list:
                if isinstance(fragment, str):
                    fragments.append(fragment)
                else:
                    # 处理 bytes
                    if encoding is None or encoding.lower() in ['unknown-8bit', '8bit', '']:
                        # 尝试用 utf-8 解码，失败则用 latin1（能解任何字节）
                        try:
                            fragments.append(fragment.decode('utf-8', errors='replace'))
                        except:
                            fragments.append(fragment.decode('latin1', errors='replace'))
                    else:
                        try:
                            fragments.append(fragment.decode(encoding, errors='replace'))
                        except (LookupError, UnicodeDecodeError):
                            # 如果编码不支持，fallback 到 latin1
                            fragments.append(fragment.decode('latin1', errors='replace'))
            return ''.join(fragments)
        except Exception as e:
            # 最后 fallback
            return str(header)

    def search_email_by_date_and_parse_email(self,start_dt:str, end_dt:str) -> ResultObj:
        """

        :param start_dt: YYYY-MM-DD
        :param end_dt: YYYY-MM-DD
        :return:
        """
        _start_dt = DatePack.parseStr2Datetime(start_dt,DatePack.YYYY_MM_DD).strftime("%d-%b-%Y")
        _end_dt = DatePack.parseStr2Datetime(end_dt,DatePack.YYYY_MM_DD).strftime("%d-%b-%Y")
        # search_parts = [
        #     'SINCE', _start_dt,
        #     'BEFORE', _end_dt,
        #     'FROM', "mailer@shopify.com"  # ← 这里不要加引号！
        # ]
        search_criteria = f'SINCE "{_start_dt}" BEFORE "{_end_dt}"'
        # search_criteria = [f'SINCE {_start_dt}',f'BEFORE {_end_dt}',f'FROM mailer@shopify.com']
        self.logger.info(f"正在搜索邮件，条件：{search_criteria}")
        status, messages = self.mail.search(None, search_criteria)
        email_ids = messages[0].split()
        self.logger.info(f"共找到 {len(email_ids)} 封邮件")

        data_list = []
        for i, email_id in enumerate(email_ids):
            try:
                # 获取邮件内容
                _, msg_data = self.mail.fetch(email_id, "(RFC822)")
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)
                sender = self.decode_mime_header(msg.get('From'))
                if 'mailer@shopify.com' not in sender:
                    continue

                email_id_str = email_id  # 指定编码格式
                if isinstance(email_id_str, bytes):
                    email_id_str = email_id_str.decode('utf-8', errors='replace')

                # 解码主题
                subject = decode_header(msg["Subject"])[0][0]
                if isinstance(subject, bytes):
                    subject = subject.decode('utf-8', errors='replace')

                send_dt = parsedate_to_datetime(msg.get('Date')).strftime('%Y-%m-%d %H:%M:%S')

                # 获取邮件正文
                mail_body = ""
                if msg.is_multipart():
                    for part in msg.walk():
                        content_type = part.get_content_type()
                        content_disposition = str(part.get("Content-Disposition"))
                        if content_type == "text/plain" and "attachment" not in content_disposition:
                            mail_body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                            break
                else:
                    mail_body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')

                info_dict = self.parse_contact_form(mail_body)
                info_dict['email_id'] = email_id_str
                info_dict['subject'] = subject
                info_dict['send_dt'] = send_dt
                info_dict['mail_body'] = mail_body
                info_dict['sender'] = sender
                info_dict['receiver'] = self.EMAIL
                info_dict['dt'] = start_dt
                info_dict['datasyntime'] = DatePack.getCurtime()
                data_list.append(info_dict)
            except (imaplib.IMAP4.abort, ConnectionError, OSError) as e:
                return ResultObj.error(ResultObj.EXT_SYS_ERROR, f"{start_dt} - {end_dt} 处理异常：{traceback.format_exc()}")
            except Exception as e:
                return ResultObj.error(ResultObj.FATAL_ERROR, f"{start_dt} - {end_dt} 处理异常：{traceback.format_exc()}")

        return ResultObj.success(data_list)

    def parse_contact_form(self,text):
        # 定义字段的正则表达式
        # 使用非贪婪匹配 .*? 并允许跨行（re.DOTALL）
        fields = {
            'country_code': r'Country Code:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
            'name': r'Name:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
            'email': r'Email:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
            'order_no': r'Order:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
            'model': r'Model:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
            'message': r'Message:\s*(.*?)(?=\n[A-Za-z ]+:|$)',
        }

        result = {}
        # 去除首尾空白
        text = text.strip()

        for field, pattern in fields.items():
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                # 提取内容，去除首尾空白，合并内部多余空白
                value = re.sub(r'\s+', ' ', match.group(1).strip())
                if field in ('country_code','name','email','order_no','model'):
                    value = value.replace('\n',' ').replace('\r',' ').lstrip(' -').replace('  ',' ').replace('  ',' ')
                result[field] = value
            else:
                result[field] = ''

        return result

    def run_action(self,dt):
        """
        完整运行逻辑
        :param dt: YYYYMMDD
        :return:
        """
        self.init_mail_conn_obj()
        # 选择收件箱
        self.mail.select("INBOX")
        start_dt = DatePack.parseStr2Datetime(dt, DatePack.YYYYMMDD)
        self.dbs.delete(f"delete from shopify.spf_auxito_mail_contact_info where dt = '{DatePack.parseDatetime2Str(start_dt,DatePack.YYYY_MM_DD)}'")
        while start_dt < DatePack.getCurtime():
            end_dt = DatePack.addDays(start_dt,1)
            res = self.search_email_by_date_and_parse_email(DatePack.parseDatetime2Str(start_dt,DatePack.YYYY_MM_DD)
                                                          ,DatePack.parseDatetime2Str(end_dt,DatePack.YYYY_MM_DD)
                                                          )
            if res.code == ResultObj.EXT_SYS_ERROR:
                self.logger.info(f"链接异常，暂停2秒后重连")
                time.sleep(2)
                self.init_mail_conn_obj()
                self.mail.select("INBOX")
                res = self.search_email_by_date_and_parse_email(
                    DatePack.parseDatetime2Str(start_dt, DatePack.YYYY_MM_DD)
                    , DatePack.parseDatetime2Str(end_dt, DatePack.YYYY_MM_DD)
                    )
            if res.is_fail():
                self.logger.error(res.get_msg())
                break
            if len(res.get_data()) > 0:
                self.dbs.insertmysql('insert','shopify.spf_auxito_mail_contact_info',res.get_data())

            self.logger.info(f"{DatePack.parseDatetime2Str(start_dt,DatePack.YYYY_MM_DD)} - {DatePack.parseDatetime2Str(end_dt,DatePack.YYYY_MM_DD)} 采集到 {len(res.get_data())} 封有效邮件。")
            start_dt = end_dt
            time.sleep(0.1)

        self.mail.logout()


GetAliMailContactOrder('读取shopify用户上报车型数据').run_action('20240222')



