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
from email.mime.application import MIMEApplication
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
        email['From'] = self.username_sendmail
        email['To'] = ";".join(received_mail)
        try:
            smtp = smtplib.SMTP_SSL(self.mailserver, port=self.port)
            smtp.login(self.username_sendmail, self.username_authcode)
            smtp.sendmail(self.username_sendmail, ','.join(received_mail), email.as_string())
            print(f'{datetime.date.today()}日, 邮件发送成功, 收件人: {received_mail}')
            smtp.quit()
        except Exception as e:
            print(f"{datetime.date.today()}日邮件发送失败", e)

    # 添加图片附件到html模板中
    @staticmethod
    def add_img_file(img_path, image_id):
        file = open(img_path, "rb")
        img_data = file.read()
        file.close()
        img = MIMEImage(img_data)
        img.add_header('Content-ID', '<image{}>'.format(image_id))
        return img

    #  添加附件(xlsx\txt\csv\word)等
    @staticmethod
    def add_file_attachment(file_path, file_name):
        file = open(file_path, "rb")
        file_data = file.read()
        file.close()
        file_attachment = MIMEApplication(file_data)
        file_attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
        return file_attachment

    # 设置定时任务
    @staticmethod
    def timed_tasks(schedule_email):
        """定时执行：每天8：00执行一次"""
        schedule.every().day.at('08:00').do(schedule_email)
        # 开始执行任务
        while True:
            schedule.run_pending()  # 运行所有可以运行的任务
            time.sleep(60*60)  # 让程序暂停一秒钟

    # 设置一个定时任务(1分钟执行一次发送文本类型邮件)
    def send_text_email_schedule(self, text, title, received_mail):
        """此方法是自动发送文本类文件的方法，需要传入发送的文本内容：str类型，文本的标题：str类型，接收的邮箱：list类型"""
        def schedule_email():
            email = MIMEText(text, 'plain', 'utf-8')
            email["Subject"] = title
            self.send_mail(received_mail, email)
        # 执行定时任务
        self.timed_tasks(schedule_email)

    # 设置一个定时任务(1分钟执行一次：发送带附件的文本类型邮件)
    def send_attachment_email_schedule(self, file_path, text, title, received_mail):
        """
        此方法是自动发送带附件的普通文件的方法，需要传入发送的文件路径：str类型，文件名：str类型，文本内容：str类型，文本的标题：str类型，接收的邮箱：list类型
        :return:
        """
        def schedule_email():
            email = MIMEMultipart('related')  # 定义邮件的类型，related是超文本加附件的类型
            content = MIMEText(text, 'html', 'utf-8')
            email.attach(content)
            email["Subject"] = title
            for path in file_path:
                email.attach(self.add_file_attachment(path[0], path[1]))
            self.send_mail(received_mail, email)
        # 执行定时任务
        self.timed_tasks(schedule_email)

    # 设置一个定时任务(1分钟执行一次发送图文混合的html类型邮件)
    def send_html_email_schedule(self, html_file, title, img_path, received_mail):
        def schedule_email():
            # 1、生成可放文字+图片的容器
            email = MIMEMultipart('related')  # 定义邮件的类型，related是超文本加附件的类型
            content = MIMEText(html_file, 'html', 'utf-8')
            email.attach(content)
            email["Subject"] = title
            # 添加图片附件
            for path in img_path:
                email.attach(self.add_img_file(path[0], path[1]))
            # 发送邮件
            self.send_mail(received_mail, email)
        # 执行定时任务
        self.timed_tasks(schedule_email)


def main():
    print("这是程序的入口")
    auto_mail = AutoMail()
    # 发送文本邮件
    # auto_mail.send_text_email_schedule("薛之谦演唱会抢票时间：2024-04-10 17：17：00", "抢票提醒", ["1678865476@qq.com"])

    # 发送带附件的文本邮件
    # file_path = [["data/email_file/img_file/今日日报.png", "今日日报.png"]]
    # text = "这是一个带有附件的文本邮件测试脚本"
    # tile = "测试脚本"
    # received_mail = ["1678865476@qq.com"]
    # auto_mail.send_attachment_email_schedule(file_path, text, tile, received_mail)

    # 发送图文混合的html类型邮件
    month = "3月"
    html_file = open("data/email_file/html_file/日报模板.txt", "r", encoding='utf-8').read()
    date_day = datetime.datetime.today().date()
    title = f"{date_day}日报"
    img_path = [
                ["data/email_file/img_file/今日日报.png", 1],
                [f"data/email_file/img_file/{month}user_sex_pie_chart.png", 2],
                [f"data/email_file/img_file/{month}user_age_pie_chart.png", 3],
                [f"data/email_file/img_file/{month}user_lv_pie_chart.png", 4],
                [f"data/email_file/img_file/{month}user_city_lv_pie_chart.png", 5],
                [f"data/email_file/img_file/{month}user_buy_sex_pie_chart.png", 6],
                [f"data/email_file/img_file/{month}user_buy_age_pie_chart.png", 7],
                [f"data/email_file/img_file/{month}user_buy_lv_pie_chart.png", 8],
                [f"data/email_file/img_file/{month}user_buy_city_pie_chart.png", 9]
    ]
    received_mail = ["1678865476@qq.com"]
    auto_mail.send_html_email_schedule(html_file, title, img_path, received_mail)


if __name__ == '__main__':
    main()
    print("程序结束！")
