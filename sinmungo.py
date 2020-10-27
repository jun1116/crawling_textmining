from bs4 import BeautifulSoup
from selenium import webdriver
from time import sleep
import csv

SIN="https://www.epeople.go.kr/nep/pttn/gnrlPttn/pttnSmlrCaseList.npaid"

def chromeOptions():
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")
    options.add_argument("lang=ko_KR")  # 한국어!

    # UserAgent값을 바꿔주는부분
    options.add_argument(
        "user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36")

    #프록시 서버
    options.add_argument("proxy-server=localhost:8080")

    return options

def scrapping(req):
    soup = BeautifulSoup(req, 'html.parser')
    trs = soup.find('tbody').find_all('tr')
    contents=[]
    for tr in trs:
        # print(tr.td) #번호
        # print(tr.find('td',{'class','left'}).text) #제목
        tds = tr.find_all('td')
        contents.append([tds[0].text, tds[1].text, tds[2].text, tds[3].text, tds[4].text.strip()])
    return contents

def saveCsv(dict):
    keys=dict.keys()
    for key in keys:
        with open(f'./sinmungo/{key}.csv', mode='w',encoding='utf-8') as file:
            writer=csv.writer(file)
            writer.writerow(['count','title','agency','date','viewed'])
            temp=dict[key]
            for line in temp:
                writer.writerow(line)

def web(keyword,year):
    ###
    #Chrome option 지정
    #options = chromeOptions()
    #driver = webdriver.Chrome('chromedriver', chrome_options=options)
    ###
    driver = webdriver.Chrome('chromedriver')
    url=SIN
    driver.get(url)
    sleep(3) # 3초 동안 페이지 로딩 기다리기

    #키워드와 기간 입력파트
    driver.find_element_by_id('searchWord').send_keys(keyword)
    driver.find_element_by_id('rqstStDt').clear()#기존 칸에 있는 데이터 삭제
    driver.find_element_by_id('rqstStDt').send_keys(f'{year}-01-01')
    driver.find_element_by_id('rqstEndDt').clear()
    driver.find_element_by_id('rqstEndDt').send_keys(f'{year}-12-31')

    driver.find_element_by_xpath('//*[@id="frm"]/div[1]/div[1]/div[4]/button[1]').click()
    sleep(3) # 3초 동안 페이지 로딩 기다리기

    ##페이지 수 확인
    req = driver.page_source
    soup = BeautifulSoup(req, 'html.parser')
    pagenum = soup.find('span', {'class', 'paging_count'})
    pages = int(pagenum.text.split('/')[-1])
    print(f'총 페이지수 : {pages} p')
    #####

    contentslist=[]
    #for i in range(pages):
    for i in range(3):

        req = driver.page_source

        contentslist.extend(scrapping(req))

        #next page로 클릭##
        driver.find_element_by_xpath('//*[@id="frm"]/div[3]/span[4]').click()
        sleep(3)

    tmpdict={}
    tmpdict[f'{year}_{keyword}_신문고']=contentslist

    saveCsv(tmpdict)

    driver.quit()

web('트램',2020)
