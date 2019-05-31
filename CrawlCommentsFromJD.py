import requests
import json
import re
import pickle
import random
import time
import os
# this if for delete uncomplete download
import atexit
currentItemId = -1
def exit_handler():
    if currentItemId != -1:
        filename = 'comments/comments_' + str(currentItemId) + '.pkl'
        os.remove(filename)
        print('delete ' + filename)

atexit.register(exit_handler)
# sleep seconds
def wait(s=1):
    time.sleep(s)


# deal with alredy downloaded data
files = os.listdir('comments')
downloads = []
for file in files:
    if file[0] == 'c':
        lastPart = file.split('_')[1]
        id = lastPart.split('.')[0]
        downloads.append(id)

Referer = 'https://item.jd.com/100004363706.html'
User_Agent =  'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36'
headers = {'User-Agent':User_Agent, 'Referer': Referer}



search_part1 = 'https://search.jd.com/Search?keyword=%E6%89%8B%E6%9C%BA&enc=utf-8&qrst=1&rt=1&stop=1&vt=2&cid2=653&cid3=655&page='
searchPageNum = 7
search_part2 = '&s='
s = 172
search_part3 = '&click=0'
search_url = search_part1 + str(searchPageNum) + search_part2 + str(s) + search_part3
search_page = requests.get(search_url,headers=headers)
search_page.encoding = 'utf-8'
itemsHtmlRe= re.compile('J_goodsList.*?J_bottomPage', re.DOTALL)
itemsHtml = itemsHtmlRe.findall(search_page.text)[0]
itemids = re.findall('(?<=item.jd.com/).*?(?=\.html)', itemsHtml)
itemids = list(set(itemids))

item_list_filename = 'item_list/' + 'item_list_page_' + str(searchPageNum) + '.pkl'
with open(item_list_filename, 'wb') as handle:
    pickle.dump(itemids, handle)



for itemId in itemids:
    # skip item has been collected
    if itemId in downloads:
        print(itemId + 'alread downloaded')
        continue
    # for delete uncomplete
    currentItemId = itemId


    url_p1 = 'https://sclub.jd.com/comment/productPageComments.action?callback=fetchJSON_comment98vv516&productId='
    url_p2 = '&score=0&sortType=5&page='
    url_p3 = '&pageSize=10&isShadowSku=0&fold=1'
    pageNum = 1
    url = url_p1 + itemId + url_p2 + str(pageNum) + url_p3
    res = requests.get(url, headers=headers)

    commentCount = re.findall('(?<="commentCount":).*?(?=,)', res.text)[0]
    commentCount = int(commentCount)
    # only crawl item with more data
    if commentCount < 20:
        continue
    # jd only return top 100 page comments
    pageCount = min(90, commentCount//10)

    comments_file_name = 'comments/' + 'comments_' + itemId + '.pkl'
    comments_file = open(comments_file_name, 'wb')
    for pageNum in range(1, pageCount):
        url = url_p1 + itemId + url_p2 + str(pageNum) + url_p3
        res = requests.get(url, headers=headers)
        jd = json.loads(res.text.lstrip('fetchJSON_comment98vv516(').rstrip(');'))
        pickle.dump(jd, comments_file)
        print('Current comment page number: ' + str(pageNum) + '/' + str(pageCount) + ' itemId: ' + itemId)
        wait(1 + 2 * random.random())
    comments_file.close()




