#! /usr/bin/env python
#coding=utf-8

import time,os
import urllib
import urllib2
import cookielib
import MySQLdb
import smtplib
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.multipart import MIMEMultipart

screens = ["Wangfan-windows"]

save_graph_path = "%s"%time.strftime("%Y-%m-%d")

if not os.path.exists(save_graph_path):
    os.makedirs(save_graph_path)
# zabbix host
zabbix_host = "mnt.1cloudtech.com"
# zabbix login username
username = "ansible"
password = "9hvfxr1R"

width = 600
height = 100
# graph Time period, s
period = 86400

# zabbix DB
dbhost = "localhost"
dbport = 3306
dbuser = "zabbix"
dbpasswd = "M$1xYI/o*O"
dbname = "zabbix"

# mail
to_list = ['rex.wu@1cloudtech.com','nick.he@1cloudtech.com']
smtp_server = "smtp.exmail.qq.com"
mail_user = "alert@1cloudtech.com"
mail_pass = "ECLHC6UBsQFUGKjDPK2w"

def mysql_query(sql):
    try:
        conn = MySQLdb.connect(host=dbhost,user=dbuser,passwd=dbpasswd,port=dbport,connect_timeout=20)
        conn.select_db(dbname)
        cur = conn.cursor()
        count = cur.execute(sql)
        if count == 0:
            result = 0
        else:
            result = cur.fetchall()
        return result
        cur.close()
        conn.close()
    except MySQLdb.Error,e:
        print "mysql error:" ,e

def get_graph(zabbix_host,username,password,screen,width,height,period,save_graph_path):
    screenid_list = []
    filename_list = []
    global html
    html = """<table border="0">
   <tr bgcolor="#CECFAD" height="20" duokan-code-cn:14px>
    <td colspan=2>zabbix监控数据报表<a href="mnt.1cloudtech.com">更多>></a></td>
   </tr>"""
    for i in mysql_query("select screenid from screens where name='%s'"%(screen)):
                for screenid in i:
                    graphid_list = []
                    for c in mysql_query("select resourceid from screens_items where screenid='%s'"%(int(screenid))):
                        for d in c:
                            graphid_list.append(int(d))
                    for graphid in graphid_list:
                        login_opt = urllib.urlencode({
                        "name": username,
                        "password": password,
                        "autologin": 1,
                        "enter": "Sign in"})
                        get_graph_opt = urllib.urlencode({
                        "graphid": graphid,
                        "screenid": screenid,
                        "width": width,
                        "height": height,
                        "period": period})
                        cj = cookielib.CookieJar()
                        opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
                        login_url = r"http://%s/index.php"%zabbix_host
                        save_graph_url = r"http://%s/chart2.php"%zabbix_host
                        opener.open(login_url,login_opt).read()
                        data = opener.open(save_graph_url,get_graph_opt).read()
                        filename = "%s/%s.%s.png"%(save_graph_path,screenid,graphid)
#                        html += '<img width="600" height="250" src="http://%s/%s/%s/%s.%s.png">'%(zabbix_host,save_graph_path.split("/")[len(save_graph_path.split("/"))-2],save_graph_path.split("/")[len(save_graph_path.split("/"))-1],screenid,graphid)
                        html += '<tr><td><img src="cid:%s"></td></tr>'%filename
			filename_list.append(filename);
                        f = open(filename,"wb")
                        f.write(data)
                        f.close()
    html+="""</table>"""
    return filename_list

def addimg (src, imgid):
# 打开文件
    fp = open(src,'rb')
# 创建MIMEImage对象，读取图片内容并作为参数
    msgImage = MIMEImage(fp.read())
# 关闭文件
    fp.close()
# 指定图片文件的Content-ID,<img>标签src使用
    msgImage.add_header('Content-ID',imgid)
# 返回msgImage对象
    return msgImage


def send_mail(username,password,smtp_server,to_list,sub,content,filename_list):
    me = "<" + username + ">"
    msg = MIMEMultipart('related')
#    msg = MIMEText(content,_subtype="html",_charset="utf8")
    msg["Subject"] = sub
    msg["From"] = me
    msg["To"] = ";".join(to_list)
# MIMEMultpart对象附加MIMEText的内容
# 创建一个MIMEText对象，HTML元素包括表格<table>及图片<img>
    msgtext = MIMEText(html,"html","utf-8")
    msg.attach(msgtext)
    for filename in filename_list:
	msg.attach(addimg(filename,filename))
    try:
        server = smtplib.SMTP()
        server.connect(smtp_server)
        server.login(username,password)
        server.sendmail(me,to_list,msg.as_string())
        server.close()
        print "send mail Ok!"
    except Exception, e:
        print e

if __name__ == '__main__':
    for screen in screens:
        filename_list=get_graph(zabbix_host,username,password,screen,width,height,period,save_graph_path)
    send_mail(mail_user,mail_pass,smtp_server,to_list,"zabbix报表",html,filename_list)