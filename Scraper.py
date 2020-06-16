import os
import sys
import math
import time
import json
import random
import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

#初始化list
author_id_list = []
title_list = []
popularity_list = []
article_time_list = []
article_link_list = []
article_content_list = [''] * 40  #定義大小
response_page_list = [1] * 40  #先定義為1這樣當抓不到頁數時則代表只有一頁，且順便定義了大小
responser_id_list = []
response_time_list = []
response_content_list = []
article_list = []

#將User agent隨機設定
def set_header_user_agent():
    user_agent = UserAgent()
    return user_agent.random

while 1:
    try:
        article_num = int((input('請輸入欲爬取文章筆數:')))  #欲爬取的文章筆數
        print('爬蟲程式執行中...')
        break
    except ValueError:
        print('請輸入整數!')
all_page = math.ceil(article_num / 30)  #需爬取的頁數

for page in range(all_page):  #爬取應爬的頁數
    user_agent = set_header_user_agent()  #替換UA
    next_url = 'https://www.mobile01.com/topiclist.php?f=383&p=' + str(page+1)
    url = next_url
    res = requests.get(url, headers={ 'user-agent': user_agent })  #以GET的方式取得URL原始碼，將假UA寫入Headers使網頁錯判為一般使用者
    soup = BeautifulSoup(res.text, 'lxml')  #將抓到的資料解析成原始碼，lxml為官方推薦的解析器

    #取得文章作者ID
    author_id = soup.select('div a.c-link.u-ellipsis')  #篩選文章作者ID
    for a_id in author_id:
        author_id_list.append(a_id.text)

    #取得文章標題
    title = soup.select('div.c-listTableTd__title a.c-link.u-ellipsis')  #也可叫出文章連結 print(name['href'])
    for title in title:
        title_list.append(title.text)
    
    #取得文章人氣
    popularity = soup.select('div.l-listTable__td--count div.o-fMini')
    for popu in popularity:
        popularity_list.append(popu.text)
    
    #取得文章時間
    article_time = soup.select('div.l-listTable__td--time div.o-fNotes')
    for a_time in article_time:
        article_time_list.append(a_time.text)
    
    #取得文章連結
    article_link = soup.select('div.c-listTableTd__title a.c-link.u-ellipsis')
    for a_link in article_link:
        article_link_list.append('https://www.mobile01.com/' + a_link['href'])

#將多餘的資料去除
author_id_list = author_id_list[1::3]  #第二個資料開始，間隔兩個抓一次資料
author_id_list = author_id_list[:article_num]  #只取指定文章筆數

title_list = title_list[:article_num]

popularity_list = popularity_list[:article_num]
popularity_list[:] = [int(x) for x in popularity_list]  #將str的list轉成int的list
sorted_article_list = sorted(range(len(popularity_list)), key = lambda k : popularity_list[k], reverse=True)
#將文章人氣list的index值提出然後依照key值從大到小排序後存成新的list

article_time_list = article_time_list[::2]  #第一項資料開始，間隔一個抓一次資料
article_time_list = article_time_list[:article_num]

article_link_list = article_link_list[:article_num]

#取得特定筆數文章資訊
for sorted_a in sorted_article_list:  #用文章人氣排序過的list依序請求各個文章的資料
    article_url = article_link_list[sorted_a]
    user_agent = set_header_user_agent()
    #time.sleep(random.uniform(0, 1))  #程式暫停0~1秒(被偵測為爬蟲而斷線時使用)
    article_res = requests.get(article_url, headers={ 'user-agent': user_agent })
    article_soup = BeautifulSoup(article_res.text, 'lxml')

    #取得前40篇特定文章內文
    content_temp_list = []  #宣告一個暫存list
    article_content = article_soup.select('article.l-publishArea.topic_article')  #另一種寫法:article_content = article_soup.find('div', {'itemprop':'articleBody'})
    for a_content in article_content:
        content_temp_list.append(a_content.text.replace('\xa0', ' ').strip())  #text取文字，replace取代\xa0為空白，strip()去除前後空白
        article_content_list[sorted_a] = content_temp_list[0]  #將篩選完的內文寫入文章所代表的index位置

    #取得特定文章回覆總頁數
    response_page_temp_list = []
    response_page = article_soup.select('li.l-pagination__page a.c-pagination')
    for response_p in response_page:
        response_page_temp_list.append(response_p.text)  #將文章回覆的頁數數字從1寫到最後
    response_page_temp_list = response_page_temp_list[-1:]  #只取最後一個資料(也就是最後一頁的數字)
    response_page_temp_list[:] = [int(x) for x in response_page_temp_list]  #把list內string轉成int
    if response_page_temp_list != []:  #如果沒有抓不到頁數則代表不只一頁(抓不到可能是沒人回覆或回覆量不到第二頁)
        response_page_list[sorted_a] = response_page_temp_list[0]  #將回覆頁數寫入list

    #取得特定文章所有回覆資訊
    for r_p_l in range(response_page_list[sorted_a]):  #從0~當前文章最後回覆頁數
        responsed_url = article_link_list[sorted_a] + '&p=' + str(r_p_l+1)  #替換回覆頁數
        user_agent = set_header_user_agent()
        responsed_res = requests.get(responsed_url, headers={ 'user-agent': user_agent })
        soup_message = BeautifulSoup(responsed_res.text, 'lxml')

        responser_id = soup_message.select('div.c-authorInfo__id a.c-link.c-link--gn.u-ellipsis')  #篩選回覆者ID
        response_time = soup_message.select('div.l-navigation__item span.o-fNotes.o-fSubMini')  #篩選回覆時間
        [block.extract() for block in soup_message('blockquote')]  #移除blockquote標籤
        response_content = soup_message.select('article.u-gapBottom--max.c-articleLimit')  #篩選回覆內容

        for r_id in responser_id:  #將回覆者ID寫入list
            responser_id_list.append(r_id.text.replace('\n', '').strip())
        for r_time in response_time:  #將回覆時間寫入list
            response_time_list.append(r_time.text)
        for r_content in response_content:  #將回覆內容寫入list
            response_content_list.append(r_content.text.replace('\n', '').strip())

    responser_id_list = responser_id_list[1:]  #把作者ID移除(從第二筆資料開始取)
    response_time_list = response_time_list[2::2]  #把多餘的時間內容移除(從第三筆資料開始取，間隔一個取一次)

    #所有回覆
    all_response_content = [] #將所有回覆做成list(因為for loop 所以換下一篇文章時會reset)
    for i in range(len(responser_id_list)):  #依照回覆者的個數依序寫入資料
        all_response_content.append(
            {
            '回覆者ID': responser_id_list[i],
            '時間': response_time_list[i],
            '內容': response_content_list[i]
            }
        )

    #將這些list清除(不然之後會重複寫入到article)
    responser_id_list.clear()
    response_time_list.clear()
    response_content_list.clear()

    #將全部資料包裝成一個list
    article_list.append(
        {
        '作者ID': author_id_list[sorted_a],
        '標題': title_list[sorted_a],
        '文章人氣': popularity_list[sorted_a],
        '時間': article_time_list[sorted_a],
        '內文': article_content_list[sorted_a],
        '所有回覆': all_response_content
        }
    )

article_json = json.dumps(article_list, indent=4, ensure_ascii=False)  #將article_list轉成json格式
code_dir_path = os.path.split(os.path.abspath(sys.argv[0]))[0] + '\\'  #取得執行程式之所在路徑
print(article_json, file = open(code_dir_path +'Mobile01_Scraper.json', 'w', encoding='utf-8'))  #將article_json輸出，且使用UTF-8編碼
print('爬蟲結束!!')