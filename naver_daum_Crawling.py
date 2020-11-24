import requests
import csv
from bs4 import BeautifulSoup
from time import sleep
import pandas as pd

def mknaverURL(how,keyword,year,pagenum):
    if how=='blog': #30개 단위 페이지 렌더링
        site='post'
        page=(pagenum-1)*30 + 1
    elif how=='news': # 10개 단위 페이지 렌더링
        site='news'
        page=(pagenum-1)*10 + 1
    elif how =='cafe': # 10개 단위 페이지 렌더링
        site='article'
        page=(pagenum-1)*10 + 1
    url=f'https://search.naver.com/search.naver?where={site}&sm=tab_jum&query={keyword}&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom{year}0101to{year}1231&start={page}'
    return url


# 네이버 사이트 중 카페블로그가 VIEW라는 항목으로 묶이기 전 크롤러
def OldnaverCrawling(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')

    if url[44:48] == 'news':  # news
        lis = soup.select("#main_pack > div.news.mynews.section._prs_nws > ul")[0].select('li')  # news
    else:  # cafe or blog
        lis = soup.select("#elThumbnailResultArea > li")
    # _view_review_body_html > div > more-contents > div > ul

    tmplist = []
    for li in lis:
        try:  # 뉴스의경우, 작은 li들을 만들어서 그곳마저 크롤링시도를 하려는걸 방지
            title = li.dl.dt.a.text  # title
            if title == '':  # 간혹 title이 따라오지 않는 경우에 대한 처리
                title = li.dl.dt.a.text
            link = li.dl.dt.a['href']  # link
            text = li.dl.find_all('dd')[1].text  # text

            if url[44:48] == 'news':  # news date
                date = li.dl.dd.text.split(' ')[2]
            else:  # cafe, blog
                date = li.dl.dd.text  # date
            # date=li.dl.find_all('dd')[0].text #cafe blog date


        except:
            continue

        # title에 대한 간단한 텍스트 전처리
        title = title.replace(',', '').replace('.', '').replace(':', '').replace('(', '').replace(')', '').replace('[',
                                                                                                                   '').replace(
            ']', '').replace('-', '').replace('+', '').replace('ㅠ', '').replace('?', '')
        # text본문에 대한 간단한 텍스트 전처리
        text = text.replace(',', '').replace('.', '').replace(':', '').replace('ㅠ', '').replace('(', '').replace(')',
                                                                                                                 '').replace(
            '[', '').replace(']', '').replace('-', '').replace('+', '').replace('?', '')
        # title, link, text, date 폼 유지하기!
        tmplist.append([title, link, text, date])

    return tmplist


def naverCrawling(url):
    result = requests.get(url)
    soup = BeautifulSoup(result.text, 'html.parser')
    tmplist = []
    if url[44:48] == 'news':  # news
        ul = soup.select('#main_pack > section.sc_new.sp_nnews._prs_nws > div > div.group_news > ul')
        lis = ul[0].select('li')
        for li in lis:
            try:
                title = li.select(' div > div > a')[0].text  # title
                text = li.select('div > div > div.news_dsc > div > a')[0].text  # text
                link = li.select('div.news_wrap.api_ani_send > div > a')[0]['href']  # link
                date = li.select('div > div > div.news_info > div > span')[0].text  # date
            except:
                continue

            # title에 대한 간단한 텍스트 전처리
            title = title.replace(',', '').replace('.', '').replace(':', '').replace('(', '').replace(')', '').replace(
                '[', '').replace(']', '').replace('-', '').replace('+', '').replace('ㅠ', '').replace('?', '')
            # text본문에 대한 간단한 텍스트 전처리
            text = text.replace(',', '').replace('.', '').replace(':', '').replace('ㅠ', '').replace('(', '').replace(
                ')', '').replace('[', '').replace(']', '').replace('-', '').replace('+', '').replace('?', '')
            # title, link, text, date 폼 유지하기!
            tmplist.append([title, link, text, date])

    else:  # cafe or blog
        ul = soup.select('#_view_review_body_html > div > more-contents > div > ul')
        lis = ul[0].select('li')
        for li in lis:
            title = li.select('a.api_txt_lines.total_tit')[0].text  # title
            link = li.select('a.api_txt_lines.total_tit')[0]['href']  # link
            text = li.select('div > div.total_group > div > a > div')[0].text  # text
            date = li.select('div > div.total_sub > span > span > span.etc_dsc_area > span')[0].text  # date

            # title에 대한 간단한 텍스트 전처리
            title = title.replace(',', '').replace('.', '').replace(':', '').replace('(', '').replace(')', '').replace(
                '[', '').replace(']', '').replace('-', '').replace('+', '').replace('ㅠ', '').replace('?', '')
            # text본문에 대한 간단한 텍스트 전처리
            text = text.replace(',', '').replace('.', '').replace(':', '').replace('ㅠ', '').replace('(', '').replace(
                ')', '').replace('[', '').replace(']', '').replace('-', '').replace('+', '').replace('?', '')
            # title, link, text, date 폼 유지하기!
            tmplist.append([title, link, text, date])
    return tmplist

#how = 방식, keyword = 키워드 , year = 연도, pages = 몇페이지할지
def naver(how,keyword,year,pages):
    tmpp=[]
    for page in range(pages):
        url= mknaverURL(how,keyword,year,page)
        tmpp.extend(naverCrawling(url))
    tmpdict={}
    tmpdict[f'{year}_{keyword}'] = tmpp
    #saveCsv(tmpdict)
    return tmpdict

def saveCsv(Dict):
    keys = Dict.keys()
    for key in keys:
        # Colab ('/content/drive/My Drive/Colab Notebooks/test/')
        #file = open(f'/content/drive/My Drive/Colab Notebooks/test/{key}.csv' ,mode = 'w')
        # LOCAL
        with open(f'./data/{key}.csv' ,mode = 'w',encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['title','link','text','date'])
            temp = Dict[key]
            for line in temp:
                writer.writerow(line)
#naver('blog','시내버스','2020',50)
# naver('blog','시외버스','2019',30)
# naver('blog','광역버스','2019',30)
# naver('blog','고속버스','2019',30)
# naver('blog','택시','2019',30)
# naver('blog','지하철','2019',30)
# naver('blog','철도','2019',30)
# naver('blog','KTX','2019',30)
# naver('blog','도시철도','2019',30)
# naver('blog','전철','2019',30)
## 2020-11-03 // 00:30
# naver('news','시외버스','2019',50)
# naver('news','광역버스','2019',50)
# naver('news','고속버스','2019',50)
# naver('news','택시','2019',50)
# naver('news','지하철','2019',50)
# naver('news','철도','2019',50)
# naver('news','KTX','2019',50)
# naver('news','도시철도','2019',50)
# naver('news','전철','2019',50)

# 2020-11-03 // 00:45
# naver('news','시외버스','2020',50)
# naver('news','광역버스','2020',50)
# naver('news','고속버스','2020',50)
# naver('news','택시','2020',50)
# naver('news','지하철','2020',50)
# naver('news','철도','2020',50)
# naver('news','KTX','2020',50)
# naver('news','도시철도','2020',50)
# naver('news','전철','2020',50)

# 2020-11-04__news 2020,2019 시내버스 키워드 수집
# naver('news','시내버스','2019',50)
# naver('news','시내버스','2020',50)

###################################
def mkdaumURL(how, keyword, year, pagenum):
    # url=f'https://search.naver.com/search.naver?where={site}&sm=tab_jum&query={keyword}&nso=so%3Ar%2Ca%3Aall%2Cp%3Afrom{year}0101to{year}1231&start={page}'
    url = f'https://search.daum.net/search?w={how}&nil_search=btn&DA=NTB&enc=utf8&q={keyword}&sd={year}0101000000&ed={year}1231235959&page={pagenum + 1}&period=u'
    return url

def daumCrawling(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36'}
    sleep(1) #너무 빠른 페이지 크롤링을 막기위해 2초 간격을 둠
    result = requests.get(url, headers=headers)
    soup = BeautifulSoup(result.text, 'html.parser')
    tmplist = []

    # url[33:37]
    ul = soup.select(f'#{url[33:37]}Coll > div.coll_cont')[0].ul
    lis = ul.find_all('li')
    for li in lis:
        try: #daum blog 본문 없는 글 발견 hot-fix(삭제된글)
            tmp = li.find('div', {'class': 'cont_inner'})
            title = tmp.div.text.replace('\n', '')
            link = tmp.div.a['href']
            text = tmp.p.text.strip()
            date = tmp.span.text.strip()
        except:
            print(url,li.find('div', {'class': 'cont_inner'}).div.text)
            continue

        # title에 대한 간단한 텍스트 전처리
        title = title.replace(',', '').replace('.', '').replace(':', '').replace('(', '').replace(')', '').replace(
            '[', '').replace(']', '').replace('-', '').replace('+', '').replace('ㅠ', '').replace('?', '')
        # text본문에 대한 간단한 텍스트 전처리
        text = text.replace(',', '').replace('.', '').replace(':', '').replace('ㅠ', '').replace('(', '').replace(
            ')', '').replace('[', '').replace(']', '').replace('-', '').replace('+', '').replace('?', '')
        # title, link, text, date 폼 유지하기!
        tmplist.append([title, link, text, date])
    return tmplist

#how = 방식, keyword = 키워드 , year = 연도, pages = 몇페이지할지
def daum(how,keyword,year,pages):
    tmpp=[]
    for page in range(pages):
        pageurl= mkdaumURL(how,keyword,year,page)
        tmpp.extend(daumCrawling(pageurl))
    tmpdict={}
    tmpdict[f'{year}_{keyword}'] = tmpp
    saveCsv(tmpdict,how)
    return tmpdict

# daum('blog','시내버스',2019,50) #1102__23:18_재실행
# daum('blog','시외버스',2019,50)
# daum('blog','광역버스',2019,50) #11/2 22:28 처리
# daum('blog','고속버스',2019,50)
# daum('blog','택시',2019,50)
# daum('blog','지하철',2019,50)
# daum('blog','철도',2019,50)
# daum('blog','KTX',2019,50)
# daum('blog','도시철도',2019,50)
# daum('blog','전철',2019,50) #11/2 22:30 처리
###
# daum('blog','시내버스',2020,50)
# daum('blog','시외버스',2020,50)
# daum('blog','광역버스',2020,50)
# daum('blog','고속버스',2020,50)
# daum('blog','택시',2020,50)
# daum('blog','지하철',2020,50)
# daum('blog','철도',2020,50)
# daum('blog','KTX',2020,50)
# daum('blog','도시철도',2020,50)
# daum('blog','전철',2020,50) #11/2 22:30 처리
###
# daum('cafe','시내버스',2019,50)
# daum('cafe','시외버스',2019,50)
# daum('cafe','광역버스',2019,50) #11/2 22:28 처리
# daum('cafe','고속버스',2019,50)
# daum('cafe','택시',2019,50)
# daum('cafe','지하철',2019,50)
# daum('cafe','철도',2019,50)
# daum('cafe','KTX',2019,50)
# daum('cafe','도시철도',2019,50)
# daum('cafe','전철',2019,50) #11/2 22:30 처리
###
###_1102_23:18
# daum('cafe','시내버스',2020,50)
# daum('cafe','시외버스',2020,50)
# daum('cafe','광역버스',2020,50)
# daum('cafe','고속버스',2020,50)
# daum('cafe','택시',2020,50)
# daum('cafe','지하철',2020,50)
# daum('cafe','철도',2020,50)
# daum('cafe','KTX',2020,50)
# daum('cafe','도시철도',2020,50)
# daum('cafe','전철',2020,50)
##
##1103__00:02실행
# daum('news','시내버스',2019,50)
# daum('news','시외버스',2019,50)
# daum('news','광역버스',2019,50)
# daum('news','고속버스',2019,50)
# daum('news','택시',2019,50)
# daum('news','지하철',2019,50)
# daum('news','철도',2019,50)
# daum('news','KTX',2019,50)
# daum('news','도시철도',2019,50)
# daum('news','전철',2019,50)
# ##
## 00:12:32 2020-11-03
# daum('news','시내버스',2020,50)
# daum('news','시외버스',2020,50)
# daum('news','광역버스',2020,50)
# daum('news','고속버스',2020,50)
# daum('news','택시',2020,50)
# daum('news','지하철',2020,50)
# daum('news','철도',2020,50)
# daum('news','KTX',2020,50)
# daum('news','도시철도',2020,50)
# daum('news','전철',2020,50)