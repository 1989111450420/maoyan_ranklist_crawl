import re
import json
import requests
import time
import random
from multiprocessing import Pool

MAXSLEEP = 3
MINSLEEP = 1
STATUS_OK = 200
MAX_PAGE_NUM = 10
SERVER_ERROR_MIN = 500
SERVER_ERROR_MAX = 600
CLIENT_ERROR_MIN = 500
CLIENT_ERROR_MAX = 600

def get_one_page(URL, num_retries=5):

    if num_retries == 0:
        return None
    ua_headers = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                               '(KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36'}
    response = requests.get(URL, headers = ua_headers)
    if response.status_code == STATUS_OK:
        return response.text
    elif SERVER_ERROR_MIN <= response.status_code < SERVER_ERROR_MAX:
        time.sleep(MINSLEEP)
        get_one_page(URL, num_retries - 1)
    elif CLIENT_ERROR_MIN <= response.status_code < CLIENT_ERROR_MAX:
        if response.status_code == 404:
            print('page not found')
        elif response.status_code == 403:
            print('have no rights')
        else:
            pass
    return None


def parse_one_page(html):

    pattern = re.compile('<p class="name"><a href="/films/[\s\S]*?" '
                         'title="([\s\S]*?)"[\s\S]*?<p class="star">([\s\S]*?)</p>'
                         '[\s\S]*?<p class="releasetime">([\s\S]*?)</p>')
    items = re.findall(pattern, html)
    for i in items:
        yield {
            "titlei":i[0].strip(),
            "actor":i[1].strip(),
            "time":i[2].strip()
        }

def write_to_file(item):

    # w 會覆蓋掉下筆資料 a 則是向後追加
    with open('貓眼.txt', 'a', encoding='utf-8') as f:
        f.write(json.dumps(item, ensure_ascii=False) + '\n')

def crawl_one_page(offset=0):
    url = 'https://maoyan.com/board/'
    html = get_one_page(url)
    for i in parse_one_page(html):
        write_to_file((i))
    # time.sleep(random.randint(MINSLEEP, MAXSLEEP))

if __name__ == '__main__':
    for i in range(MAX_PAGE_NUM):
        pool = Pool(2)
        pool.map(crawl_one_page, [i for i in range(10)])
        pool.close()
        pool.join()

