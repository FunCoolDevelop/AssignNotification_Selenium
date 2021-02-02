from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from django.utils import timezone
from .models import Assign, College, Student, Course, Quiz, TeamPro
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from asgiref.sync import sync_to_async, async_to_sync
from time import sleep
from datetime import datetime
import time, datetime
import asyncio

def index(request) :
    students = Student.objects.all()
    return render(request, 'index.html',{"students":students})

def crawlSingle(request,stid) :
    sid = int(stid)
    student = Student.objects.filter(Q(id=sid)).get()
    sync_to_async(operation(sid,student),thread_sensitive=True)
    return render(request, 'crawlPage.html',{"name":student.name})

def crawlAll(request) :
    students = Student.objects.all()
    sync_to_async((operation(-1,students)),thread_sensitive=True)
    return render(request, 'crawlPage.html',{"name":"All"})

def operation(sid,stObj) :
    if sid == -1 :
        for i in stObj :
            crawl(i)
    else :
        crawl(stObj)

def crawl(student):
    start = time.time()
    ## crawlTemp(student) # 학기중엔 crawlTemp 사용x

    print('Crawling account name [' + student.name + ']' + ' / ' + (str)(datetime.datetime.now()))
    # login
    college = College.objects.filter(Q(id=student.college_id)).get()
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1280,720')

    driver = webdriver.Chrome(r"C:/chromedriver.exe", options=options)
    driver.implicitly_wait(1)

    driver.get(url=college.home_url)

    id_input = driver.find_element_by_id('usr_id')
    id_input.send_keys(student.login_id)

    pw_input = driver.find_element_by_id('usr_pwd')
    pw_input.send_keys(student.login_pw)

    login_btn = driver.find_element_by_id('login_btn')
    login_btn.click()
    #
    # crawl course(lesson) in main page
    lessons = driver.find_elements_by_class_name('sub_open')
    sub_len = len(lessons)
    # crawl assign
    assignList = []
    for i in range(0,sub_len) :
        tmpList = []
        
        lessons = driver.find_elements_by_class_name('sub_open')
        lns = lessons[i]

        print("Course " + (str)(i + 1) + "    " + lns.text)
        tmpList.append(lns.text)
        
        try :
            lns.click()
            homw_tab = driver.find_element_by_id('menu_report')
            homw_tab.click()

            names = driver.find_elements_by_class_name("subjt_top")
            dates = driver.find_elements_by_class_name("number")
            
            if names == None :
                l = 0
            else :
                l = len(names)

            for j in range(0,l):
                    nn = names[j].text # name
                    ns = dates[((j+1)*5) - 2].text # score
                    nd = dates[((j+1)*5) - 1].text # date
                    tmp = []
                    tmp.append(nn)
                    tmp.append(ns)
                    tmp.append(nd)
                    tmpList.append(tmp)
        except : # 과제가 없는 과목도 assignList에 제목은 추가됨
            i = i

        assignList.append(tmpList)
        driver.back()
        driver.back()

    #print('Crawling Finished')

    result = ''
    for i in assignList : # string transformation
        ilen = len(i)
        result += i[0] + '\n'
        for j in range(1,ilen) :
            result += i[j][0] + '  |  ' + i[j][1] + '  |  ' + i[j][2] + '\n'
        result += '\n'
    #print(result)

    driver.close()
    postProcess(student,assignList)
    start = time.time() - start
    times = str(datetime.timedelta(seconds = start)).split('.')
    times = times[0]
    print('Time taken : ' + times)

def crawlTemp(student): # 학기중이 아니므로 다른 경로로 크롤링
    print('Crawling account name [' + student.name + ']' + ' / ' + (str)(datetime.datetime.now()))
    # login
    college = College.objects.filter(Q(id=student.college_id)).get()
    options = webdriver.ChromeOptions()
    options.add_argument('window-size=1280,720')

    driver = webdriver.Chrome(r"C:/chromedriver.exe", options=options)
    driver.implicitly_wait(1)

    driver.get(url=college.home_url)

    id_input = driver.find_element_by_id('usr_id')
    id_input.send_keys(student.login_id)

    pw_input = driver.find_element_by_id('usr_pwd')
    pw_input.send_keys(student.login_pw)

    login_btn = driver.find_element_by_id('login_btn')
    login_btn.click()
    #
    # 수강과목 페이지 접속
    courseBtn = driver.find_elements_by_class_name('icon-nm')
    courseBtn[0].click()
    #
    lessons = driver.find_elements_by_class_name('content-title')
    sub_len = len(lessons)
    # crawl assign
    assignList = []
    for i in range(0,sub_len) :
        tmpList = []
        
        lessons = driver.find_elements_by_class_name('content-title')
        lns = lessons[i]

        try :
            #print("Course " + (str)(i + 1) + "    " + lns.text)
            tmpList.append(lns.text)
            lns.click()
            homw_tab = driver.find_element_by_id('menu_report')
            homw_tab.click()

            names = driver.find_elements_by_class_name("subjt_top")
            dates = driver.find_elements_by_class_name("number")
            
            if names == None :
                l = 0
            else :
                l = len(names)

            for j in range(0,l):
                nn = names[j].text # name
                ns = dates[((j+1)*5) - 2].text # score
                nd = dates[((j+1)*5) - 1].text # date
                tmp = []
                tmp.append(nn)
                tmp.append(ns)
                tmp.append(nd)
                tmpList.append(tmp)
            assignList.append(tmpList)

            driver.back()
            driver.back()
        except :
            break

    #print('Crawling Finished')

    result = ''
    for i in assignList : # string transformation
        ilen = len(i)
        result += i[0] + '\n'
        for j in range(1,ilen) :
            result += i[j][0] + '  |  ' + i[j][1] + '  |  ' + i[j][2] + '\n'
        result += '\n'
    #print(result)

    driver.close()
    postProcess(student,assignList)

def postProcess(student,assignRes):
    # assignRes의 각 행 0번째 값은 과목의 이름
    # assignRes의 각 행 1번째부터 값이 존재하지 않으면 과제가 없는 과목
    courseQuery(student,assignRes)
    assignQuery(student,assignRes)

def courseQuery(student,assignRes):
    collegeId = student.college_id
    courseLs = ''
    sub_len = len(assignRes)
    for i in range(0, sub_len):
        nName = assignRes[i][0]
        try:
            tmp = Course.objects.filter(Q(college_id=collegeId) & Q(name=nName)).get()
        except :
            tmp = Course.objects.create(college_id = collegeId,name = nName, professor = '')
        courseLs += (str)(tmp.id) + ';'
    student.course_ids = courseLs
    student.save()

def assignQuery(student, assignRes) :
    collegeId = student.college_id
    courseIds = student.course_ids
    courseIds = courseIds.split(';')

    sub_len = len(courseIds)
    for i in range(0,sub_len - 1) :
        nowId = courseIds[i]
        nowAssign = assignRes[i]
        try:
            tmpset = Assign.objects.all()
            tmpset = tmpset.filter(Q(course_id=nowId))
            tmpset.delete()
        except :
            i = i

        assignLen = len(nowAssign)
        for j in range(1,assignLen) :
            date = changeFormat(nowAssign[j][2])
            tmp = Assign.objects.create(course_id = nowId,name = nowAssign[j][0], grade = nowAssign[j][1], dead_line = date)
        
def changeFormat(res) :
    res = res.split(' ')
    date = res[0].split('.')
    time = res[2].split(':')
    if res[1] == '오후' :
        tmp = (int)(time[0]) + 12
        if tmp == 24 :
            tmp = 0
        time[0] = (str)(tmp)
    date.append(time[0])
    date.append(time[1])
    #print(date)
    cr_date = datetime.datetime((int)(date[0]), (int)(date[1]), (int)(date[2]), (int)(date[3]), (int)(date[4]), 0, 0)
    date = cr_date.strftime("%Y-%m-%d %H:%M:%S.%f")
    return date