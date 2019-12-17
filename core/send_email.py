import smtplib
from email.mime.text import MIMEText
from email.header import Header
import sys

def run(prefix,dir):
    mail_host = "smtp.exmail.qq.com"
    message = MIMEText('%s项目已经运行完成,共享目录是%s'%(prefix,dir), 'plain', 'utf-8')
    message['From'] = Header("生物信息组", 'utf-8')  #发送者
    message['To'] = Header("遗传咨询组", 'utf-8')  #接收者
    ##########################邮件主题######################
    subject = 'panel27项目%s分析结果'%(prefix)
    message['Subject'] = Header(subject, 'utf-8')
    sender 		="yucaifan@chosenmedtech.com"
    password 	="Fyc240290"
    receivers="fanyucai1@126.com"
    try:
        smtpObj = smtplib.SMTP(mail_host,25)
        smtpObj.login(sender, password)
        smtpObj.sendmail(sender, receivers, message.as_string())
        print("邮件发送成功")
    except smtplib.SMTPException:
        print("Error: 无法发送邮件")

if __name__=="__main__":
    prefix=sys.argv[1]###项目名称
    dir=sys.argv[2]####共享目录
    run(prefix,dir)