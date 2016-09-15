#!/usr/bin/python
# -*- coding=utf-8 -*-

__author__ = 'smartjinyu'
import requests
import os
from PIL import Image
import cStringIO
import shelve
import sys
import getpass


def login():
    id = raw_input('Please input your student id:')
    pwd = getpass.getpass('Please input the corresponding password:')
    loginUrl = 'http://bkxk.xmu.edu.cn/xsxk/login.html'
    localInfoUrl = 'http://bkxk.xmu.edu.cn/xsxk/localInfo.html'
    session = requests.session()
    captcha_img = session.get('http://bkxk.xmu.edu.cn/xsxk/getCheckCode')
    img = cStringIO.StringIO(captcha_img.content)
    image = Image.open(img)
    image.show()
    captcha = raw_input('Please input the captcha:')
    loginData = {
        'username': id,
        'password': pwd,
        'checkCode': captcha,
    }
    html = session.post(loginUrl,loginData)
    if u'进入学生选课系统' in html.text:
        print 'Login successfully!'
        session.get(localInfoUrl)
        return session
    elif u'用户名或密码错误' in html.text:
        print 'Wrong id or password, please try again!'
        print
        login()
    elif u'验证码错误' in html.text:
        print 'Wrong captcha, please try again!'
        print
        login()
    else:
        print 'Login failed, please try again!'
        print
        login()



def printCurCourse():
    data = shelve.open('courses.data')
    num = data['num']
    i = 1
    while i <= int(num):
        print '[' + str(i) + '] ',
        print 'CourseId: '+ data[str(i)]['cid']+'  Type:'+data[str(i)]['type']
        i+=1
    return data

def start():
    if os.path.isfile('courses.data'):
        data = shelve.open('courses.data')
        num = data['num']
        data.close()
        if num == '0':
            os.remove('courses.data')
    num = raw_input('Please input the code of the action you want to take:\n[1] Specify which course you want to take\n[2] Try to take courses automatically\n[3] Reset all your settings\n[4] Exit\n')
    if num == '1':
        print
        action1()
    elif num == '2':
        print
        action2(0)
    elif num == '3':
        if os.path.isfile('courses.data'):
            os.remove('courses.data')
        print 'Done!'
        print
        start()
    elif num == '4':
        sys.exit()
    else:
        print 'Wrong code!'
        print
        start()



def action1():
    if os.path.isfile('courses.data'):#courses have already existed
        mode = 0
        data = printCurCourse()
        print 'Above are the courses you want to take. You can input the code before it to delete the course from the list.'
        print 'Note: Course Type 1 represents Quan Xiao Xing Bi Xiu Ke, 2 represents Yuan Xi Bi Xiu Ke, 3 represents Quan Xiao Xing Xuan Xiu Ke, 4 represents Yuan Xi Xuan Xiu Ke, 5 represents Gong Gong Ke.'
        print
    else:#courses do not exist
        mode = 1
        data = shelve.open('courses.data')
        data['num'] = '0'
        data.sync()
    #print the course in the file
    num = data['num']
    print 'Please input the following code to continue:'
    if mode == 0:
        code = raw_input('[A] Add a new course to the list.\n[B] Back to the main page.\n[X] Delete the course X from above list.\n')
    else:
        code = raw_input('[A] Add a new course to the list.\n[B] Back to the main page.\n')
    if code >= '1' and code <= num:
        del data[num]
        num = str(int(num) - 1)
        data['num'] = num
        data.sync()
        data.close()
        if num == '0':
            os.remove('courses.data')
        print
        action1()

    elif code == 'A' or code == 'a': #add a new course
        num = str(int(num)+1)
        data['num']= num
        print 'Note: Course Type 1 represents Quan Xiao Xing Bi Xiu Ke, 2 represents Yuan Xi Bi Xiu Ke, 3 represents Quan Xiao Xing Xuan Xiu Ke, 4 represents Yuan Xi Xuan Xiu Ke, 5 represents Gong Gong Ke.'
        print
        cid = raw_input('Please input the course id:')
        ctype = raw_input('Please input the course type:')
        data[num] = {'cid':cid,'type':ctype}
        data.sync()
        data.close()
        print
        action1()
    elif code == 'B'or code =='b': #back to the main page
        data.sync()
        data.close()
        if num == '0':
            os.remove('courses.data')
        print
        start()
    else:
        print 'Wrong code!'
        data.close()
        print
        action1()


def action2(sss):
    if not os.path.isfile('courses.data'):
        print 'You should specify the course you want to take first!'
        start()
    else:
        if sss == 0:
            session = login()
        else:
            session = sss
        printCurCourse()
        print 'Above are the courses you want to take.'
        print 'Note: Course Type 1 represents Quan Xiao Xing Bi Xiu Ke, 2 represents Yuan Xi Bi Xiu Ke, 3 represents Quan Xiao Xing Xuan Xiu Ke, 4 represents Yuan Xi Xuan Xiu Ke, 5 represents Gong Gong Ke.'
        print
        xklc = raw_input('Please input the turns code of taking courses:')
        mode = raw_input('Please input the number of the mode to continue:\n'
                         '[1] Try to take course until a number of loops.\n[2] Try to take course until you stop it manually\n')
        if mode == '1':
            N = int(raw_input('Please input the number of loops:'))
            if N < 1:
                N =1
            data = shelve.open('courses.data')
            num = data['num']
            courseList = []
            i = 1
            while i <= int(num):
                courseList.append(data[str(i)])
                i += 1
            data.close()
            j=0
            while j < N:
                try:
                    k = 0
                    while k < int(num):
                        selectUrl = 'http://bkxk.xmu.edu.cn/xsxk/elect.html?method=handleZxxk&jxbid='+ courseList[k]['cid']+'&xxlx='+ courseList[k]['type']+'&xklc='+xklc
                        html = session.get(selectUrl)
                        print html.text
                        k+=1
                except requests.exceptions.RequestException:
                    print 'An error occurred!'
                j+=1
            print 'Take course ends!You may have to log out and log in again in your browser to see the results'
        elif mode =='2':
            data = shelve.open('courses.data')
            num = data['num']
            courseList = []
            i = 1
            while i <= int(num):
                courseList.append(data[str(i)])
                i += 1
            data.close()
            j = 0
            while 1:
                try:
                    k = 0
                    while k < int(num):
                        selectUrl = 'http://bkxk.xmu.edu.cn/xsxk/elect.html?method=handleZxxk&jxbid=' + courseList[k]['cid'] + '&xxlx=' + courseList[k]['type'] + '&xklc=' + xklc
                        print selectUrl
                        html = session.get(selectUrl)
                        print html.text
                        k += 1
                except requests.exceptions.RequestException:
                    print 'An error occurred!'
                j += 1
            print 'Take course ends!You may have to log out and log in again in your browser to see the results'
        else:
            print 'Wrong code!'
            action2(session)







def main():
    print 'Please read tips and guides on smartjinyu.com before using this tool.\n'
    start()


if __name__ == '__main__':
    main()