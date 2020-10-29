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
