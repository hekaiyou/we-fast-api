import smtplib
from loguru import logger
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from core.dynamic import get_apis_configs


def send_mail(to_addrs: list, subject: str, msg: MIMEBase):
    """ 发送邮件 """
    configs = get_apis_configs('bases')
    try:
        if configs.mail_smtp_use_ssl:
            mail_server = smtplib.SMTP_SSL(
                host=configs.mail_smtp_host,
                port=configs.mail_smtp_port,
            )
        else:
            mail_server = smtplib.SMTP(
                host=configs.mail_smtp_host,
                port=configs.mail_smtp_port,
            )
        mail_server.login(configs.mail_smtp_sender, configs.mail_smtp_password)
        msg['From'] = f'{configs.app_name}<{configs.mail_smtp_sender}>'
        msg['To'] = ';'.join(to_addrs)
        msg['Subject'] = subject
        mail_server.sendmail(
            from_addr=configs.mail_smtp_sender,
            to_addrs=to_addrs,
            msg=msg.as_string(),
        )
        return True
    except smtplib.SMTPAuthenticationError as e:
        logger.error(f'发送邮件异常, {e}')
        logger.debug('建议: 确认授权码是否正确')
        logger.debug('建议: 检查一下服务器地址')
    except smtplib.SMTPServerDisconnected as e:
        logger.error(f'发送邮件异常, {e}')
        logger.debug('建议: 可能需要开启 SSL 加密')
    except Exception as e:
        logger.error(f'发送邮件异常, {e}')


def send_base_mail(to_addrs, subject, text):
    """ 发送纯文本邮件 """
    send_mail(to_addrs, subject, MIMEText(text, 'plain', 'utf-8'))


def send_simple_mail(to_addrs, subject, html_text_list: list):
    """ 发送简单 HTML 邮件 """
    text = '<div>'
    for html_text in html_text_list:
        if '</' not in html_text and '>' not in html_text:
            html_text = html_text.replace(" ", "&nbsp;")
        text += f'<p>{html_text}</p>'
    text += '</div>'
    content_css = 'span {color:#d81b60;}'
    content = f'<html><head><style>{content_css}</style></head><body><div style="background:#eee; padding-top:30px; padding-bottom:30px;"><div style="width:80%;background:#fff; margin:0 auto; border-radius: 5px; overflow:hidden;"><div style="background:#d81b60;padding: 15px 35px 10px; color:#fff; font-size:16px;">{subject}</div><div id="content" style="padding: 35px 35px 60px; overflow:hidden; max-width:100%; min-height:300px;word-wrap:break-word; word-break:break-all;">{text}</div></div></div></body></html>'
    send_mail(to_addrs, subject, MIMEText(content, 'html', 'utf-8'))
