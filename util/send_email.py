import smtplib
from email.mime.text import MIMEText


class SendMail:
    def __init__(self, mail_host):
        self.mail_host = mail_host

    def send(self, title, content, sender, auth_code, receivers):
        message = MIMEText(content, 'html', 'utf-8')
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receivers)
        message["Subject"] = title
        try:
            smtp_obj = smtplib.SMTP_SSL(self.mail_host, 465)
            smtp_obj.login(sender, auth_code)
            smtp_obj.sendmail(sender, receivers, message.as_string())
            print("邮件发送成功")
        except Exception as e:
            print("邮件发送失败:{0}".format(e))

if __name__ == '__main__':
    mail = SendMail("smtp.163.com")
    sender = "a18811584679@163.com"
    receivers = ['1670456031@qq.com']
    title = "邮件测试"
    content = """
        邮件测试系统
        <a href="https://www.bilibili.com/">欢迎点击 </a>
        """

    auth_code = "JVEKPVNLIPWFMASA"
    mail.send(title, content, sender, auth_code, receivers)
