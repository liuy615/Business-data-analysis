# -*- coding: utf-8 -*
# @Time    : 2024/4/9 10:53
# @Author  : liuy
# @File    : send_email.py


"""
1. 将读取的表“trade_orders”中的数据保存在trade_orders.csv中。
2. 读取数据，确定每列数据类型，简单检查一下数据是否有缺失值，异常值等。
3. 对每个用户分组：获取用户第一次付费的时间，并向后增加30天。统计付费次数
4. 保存
"""
import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart
import time
import schedule as schedule


class AutoMail:
    def __init__(self):
        self.mailserver = 'smtp.qq.com'
        self.username_sendmail = "2268980893@qq.com"
        self.username_authcode = "ynozbwenvnugeaji"
        self.port = 465

    # 发送邮件
    def send_mail(self, received_mail, email):
        try:
            smtp = smtplib.SMTP_SSL(self.mailserver, port=self.port)
            smtp.login(self.username_sendmail, self.username_authcode)
            smtp.sendmail(self.username_sendmail, ','.join(received_mail), email.as_string())
            print(f'{datetime.date.today()}日, 邮件发送成功, 收件人: {received_mail}')
            smtp.quit()
        except Exception as e:
            print(f"{datetime.date.today()}日邮件发送失败", e)

    # 添加图片附件
    @staticmethod
    def add_img_file(img_path, image_id):
        file = open(img_path, "rb")
        img_data = file.read()
        file.close()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', '<image{}>'.format(image_id))
        return img

    # 发送普通邮件
    def mail_text(self, text, title, received_mail):
        """
        此方法是自动发送文本类文件的方法，需要传入发送的文本内容：str类型，文本的标题：str类型，接收的邮箱：list类型
        :return:
        """
        email = MIMEText(text, 'plain', 'utf-8')
        email["Subject"] = title
        email['From'] = self.username_sendmail
        email['To'] = ";".join(received_mail)
        self.send_mail(received_mail, email)

    # 发送图文混合的html类型邮件
    def mail_html(self, html_file, title, img_path, received_mail):
        """
        :param html_file: 这是一个html模板文件，需要传入文件路径
        :param title: 这是邮件的标题
        :param img_path: 这是编写html模板需要用到的图片的路径和图片的编号
        :param received_mail: 这是需要接收邮件的邮箱列表
        :return: 直接发送每日报告的html文件
        """
        # 1、生成可放文字+图片的容器
        email = MIMEMultipart('related')  # 定义邮件的类型，related是超文本加附件的类型
        content = MIMEText(html_file, 'html', 'utf-8')
        email.attach(content)
        email["Subject"] = title
        email['From'] = self.username_sendmail
        email['To'] = ";".join(received_mail)
        # 添加图片附件
        for path in img_path:
            email.attach(self.add_img_file(path[0], path[1]))
        # 发送邮件
        self.send_mail(received_mail, email)

    def send_email_schedule(self, html_file, title, img_path, received_mail):
        def send_email():
            self.mail_html(html_file, title, img_path, received_mail)
        schedule.every(1).minutes.do(send_email)
        # 开始执行任务
        while True:
            schedule.run_pending()
            time.sleep(1)


def main():
    print("这是程序的入口")
    auto_mail = AutoMail()
    # auto_mail.mail_text("薛之谦演唱会抢票时间：2024-04-10 17：17：00", "抢票提醒", ["1678865476@qq.com"])
    # 发送图片邮件
    html_file = open("data/email_file/html_file/日报模板.txt", "r", encoding='utf-8').read()
    date_day = datetime.datetime.today().date()
    title = f"{date_day}日报"
    img_path = [["data/email_file/img_file/今日日报.png", 1], ["data/email_file/img_file/user_sex_pie_chart.png", 2]]
    received_mail = ["1678865476@qq.com"]
    auto_mail.send_email_schedule(html_file, title, img_path, received_mail)


if __name__ == '__main__':
    main()
    print("程序结束！")
