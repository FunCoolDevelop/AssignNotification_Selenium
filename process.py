from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from time import sleep
import accounts

options = webdriver.ChromeOptions()
options.add_argument('window-size=1280,720')

driver = webdriver.Chrome('chromedriver', options=options)
driver.implicitly_wait(10)

driver.get(url='http://ecampus.konkuk.ac.kr/ilos/main/member/login_form.acl')

id_input = driver.find_element_by_id('usr_id')
id_input.send_keys(accounts.id)

pw_input = driver.find_element_by_id('usr_pwd')
pw_input.send_keys(accounts.pw)

login_btn = driver.find_element_by_id('login_btn')
login_btn.click()

lessons = driver.find_elements_by_class_name('sub_open')
sub_len = len(lessons)
assignList = []
for i in range(0,sub_len) :
    tmpList = [] ## tmpList[0] is name of assign
    
    lessons = driver.find_elements_by_class_name('sub_open')
    lns = lessons[i]
    print(lns.text)
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
        nn = names[j].text
        nd = dates[((j+1)*5) - 1].text
        tmp = []
        tmp.append(nn)
        tmp.append(nd)
        tmpList.append(tmp)
        ##print(nn)
        ##print(nd)
    assignList.append(tmpList)

    driver.back()
    driver.back()

print('Crawling Finished')
print(assignList)

result = ''
for i in assignList :
    ilen = len(i)
    result += i[0] + '\n'
    for j in range(1,ilen) :
        result += i[j][0] + ' ' + i[j][1] + '\n'
    result += '\n'
print(result, file=open('Assigns.txt', 'w', encoding='utf-8'))

sleep(3)
driver.close()