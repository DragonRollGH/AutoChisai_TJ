import base64
import json
import random
import smtplib
import time
from email.mime.text import MIMEText
from urllib import parse

import requests

Usr = {
    'Authorization': '',
    'studentPid': '',
    'studentName': '',
    'studentStudentno': '',
    'studentCollege': '',
    'IP': '',
    'Receivers': ''
}

class Chisai_TJ:
    def __init__(self, Usr):
        def Gen_reportDatetime():
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            return t
        def Gen_locLat():
            L = '31.28'
            return L+str(random.randint(222, 888))
        def Gen_locLng():
            L = '121.21'
            return L+str(random.randint(222, 888))
        self.session = requests.session()
        self.ifSuccess = False
        self.exp = 0
        self.IP = '58.41.205.20'
        self.Receivers = ['dr-tj@outlook.com']
        self.POST = {
            'studentPid': '',
            'studentName': '',
            'studentStudentno': '',
            'studentCollege': '',
            'locLat': Gen_locLat(),
            'locLng': Gen_locLng(),
            'locNation': '中国',
            'locProvince': '上海市',
            'locCity': '上海市',
            'locDistrict': '嘉定区',
            'healthy': '0', 'source': 'weixin,windows',
            'reportDatetime': Gen_reportDatetime(),
            'hasMoved': 'false',
            'leaveReason': '',
            'locNation1': '中国',
            'locProvince1': '上海市',
            'locCity1': '上海市'
        }
        self.headers = {
            'Host': 'tjxsfw.chisai.tech',
            'Connection': 'keep-alive',
            'Authorization': '',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.143 Safari/537.36 MicroMessenger/7.0.9.501 NetType/WIFI MiniProgramEnv/Windows WindowsWechat',
            'content-type': 'application/x-www-form-urlencoded',
            'Referer': 'https://servicewechat.com/wx427cf6b5481c866a/27/page-frame.html',
            'Accept-Encoding': 'gzip, deflate, br'
        }

        for k, v in Usr.items():
            if k == 'IP':
                self.IP = v
            elif k == 'Receivers':
                self.Receivers.append(v)
            elif k in self.POST.keys():
                self.POST[k] = v
            elif k in self.headers.keys():
                self.headers[k] = v
        if self.IP:
            self.headers['X-Forwarded-For'] = self.IP
            # pass

    def verifyToken(self):
        try:
            jwt_b64 = self.headers['Authorization'].split('.')[1]+'=='
            jwt = base64.b64decode(jwt_b64).decode('utf-8')
            exp = int(jwt[7: 17])
            now = int(time.time())
            if now > exp:
                return False
            n2e = time.localtime(exp - now)
            self.exp = n2e.tm_yday - 1
            return True
        except:
            return True

    def isActivated(self):
        Url = 'https://tjxsfw.chisai.tech/api/school_tjxsfw_student/tblStudentUsers/isActivated?studentPid={}'.format(self.POST['studentPid'])
        try:
            Requ = self.session.get(url=Url, headers=self.headers)
        except Exception as Error:
            self.Error('requestsError: isActivated\n' + str(Error))
        self.isActivatedText = Requ.text
        return Requ

    def hasDoneToday(self):
        Url = 'https://tjxsfw.chisai.tech/api/school_tjxsfw_student/yqfkLogDailyreport/hasDoneToday?studentPid={}'.format(self.POST['studentPid'])
        try:
            Requ = self.session.get(url=Url, headers=self.headers)
        except Exception as Error:
            self.Error('requestsError: hasDoneToday\n' + str(Error))
        self.hasDoneTodayText = Requ.text
        return Requ

    def v2(self):
        def Gen_contentLength(data):
            length = len(data.keys()) * 2 - 1
            total = ''.join(list(data.keys()) + list(data.values()))
            length += len(total)
            return str(length)
        Url = 'https://tjxsfw.chisai.tech/api/school_tjxsfw_student/yqfkLogDailyreport/v2'
        Headers = self.headers
        Headers['Content-Length'] = Gen_contentLength(self.POST)
        Post = parse.urlencode(self.POST).replace('+', '%20')
        try:
            Requ = self.session.post(url=Url, headers=Headers, data=Post)
        except Exception as Error:
            self.Error('requestsError: v2\n' + str(Error))
        self.v2Text = Requ.text
        return Requ

    def run(self):
        if self.verifyToken():
            if '操作成功' in self.isActivated().text:
                time.sleep(1)
                if '今日未打卡' in self.hasDoneToday().text:
                    time.sleep(3)
                    if '操作成功' in self.v2().text:
                        self.Success()
                    else:
                        self.Error('无法打卡！\n' + self.v2Text)
                elif '今日已打卡' in self.hasDoneTodayText:
                    self.Error('今日已打卡！\n')
                else:
                    self.Error('无法获取打卡状态！\n' + self.hasDoneTodayText)
            else:
                self.Error('无法连接服务器！\n' + self.isActivatedText)
        else:
            self.Error('Token已过期！\n')
        return self.ifSuccess

    def LOG(self, msg):
        with open('Chisai_TJ.log','a') as LOG:
            t = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            LOG.write(t+'  '+msg+'\n')
            print(t+'  '+msg)

    def Success(self):
        self.ifSuccess = True
        Title = '{}: 打卡成功！ '.format(self.POST['studentStudentno'])
        Content = 'Token还有{}天到期。'.format(self.exp)
        ContentEmail = 'Token还有{}天到期。'.format(self.exp)
        self.SendEmail(Title, ContentEmail)
        self.LOG(Title + Content)

    def Error(self, Error):
        Title = 'Fail: {} '.format(self.POST['studentStudentno'])
        Content = Error
        self.SendEmail(Title, Content)
        self.LOG(Title + Content)

    def SendEmail(self, title, content):
        mail_host = ""
        mail_user = ""
        mail_pass = ""

        sender = ''
        receivers = self.Receivers

        message = MIMEText(content, 'plain', 'utf-8')
        message['From'] = "{}".format(sender)
        message['To'] = ",".join(receivers)
        message['Subject'] = title

        try:
            smtpObj = smtplib.SMTP_SSL(mail_host, 465)
            smtpObj.login(mail_user, mail_pass)
            smtpObj.sendmail(sender, receivers, message.as_string())
        except smtplib.SMTPException as Error:
            Title = 'Fail to Send Email: {}'.format(self.POST['studentStudentno'])
            self.LOG(Title)

Chisais = [Chisai_TJ(Usr)]
for Chisai in Chisais:
    Chisai.run()
