import json
import requests
import random
import datetime
import csv
import pymongo
import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

client = pymongo.MongoClient("192.168.0.23", 21017)


categories = {}
with open('docs/categories.csv') as r:
    rows = csv.DictReader(r)
    for row in rows:
        categories[row['\ufeffcategory']] = row['english_name']


def translate_with_youdao(text):
    user_agent_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
        "Mozilla/5.0 (X11; CrOS i686 2268.111.0) AppleWebKit/536.11 "
        "(KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 "
        "(KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.1 "
        "(KHTML, like Gecko) Chrome/19.77.34.5 Safari/537.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.9 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 "
        "(KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 5.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_0) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
        "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 "
        "(KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 "
        "(KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
    ]
    url = f'http://fanyi.youdao.com/translate?&doctype=json&type=AUTO&i={text}'
    resp = requests.get(url, headers={
        'User-Agent': random.choice(user_agent_list)
    })
    if resp.ok:
        try:
            return resp.json()['translateResult'][0][0]['tgt']
        except Exception as e:
            return ''
    return ''


def utc_str_to_local_str(utc_str: str, utc_format: str, local_format: str):
    utc_str = utc_str.strip()
    temp1 = datetime.datetime.strptime(utc_str, utc_format)
    temp2 = temp1.replace(tzinfo=datetime.timezone.utc)
    local_time = temp2.astimezone()
    return local_time.strftime(local_format)


def load(item):
    doc = {
        'url': f"https://arxiv.org/abs/{item['id']}",
        'title': item['title'],
        # 'chinese_title': translate_with_youdao(item['title']),
        'chinese_title': '',
        'authors': [' '.join(authors[::-1]).strip() for authors in item['authors_parsed']],
        'abstract': item['abstract'].strip().replace('\n', ' '),
        'subjects': [{'name': categories[category], 'short': category} for category in item['categories'].split(' ')],
        'submissions': [{'author': item['submitter'], 'date': utc_str_to_local_str(version['created'], '%a, %d %b %Y %H:%M:%S UTC' if 'UTC' in version['created'] else '%a, %d %b %Y %H:%M:%S GMT', '%Y-%m-%d')} for version in item['versions']],
        'attachment': f"https://arxiv.org/pdf/{item['id']}.pdf"
    }
    # cursor = client.papers.arxiv.find({"url": doc['url']})
    # if cursor.count() <= 0:
    client.papers.arxiv.insert_one(doc)
    print(doc['url'])


if __name__ == "__main__":
    ids = []
    with open('arxiv.txt', 'r') as fp:
        for line in fp.readlines():
            ids.append(line.strip())

    # 线程池执行
    start_time_1 = time.time()
    with ThreadPoolExecutor(max_workers=20) as executor:
        with open('arxiv-metadata-oai-snapshot.json', 'r') as fp:
            while True:
                line = fp.readline()
                if not line:
                    break
                item = json.loads(line.strip())
                insert = True
                for id in ids:
                    if id == item['id']:
                        insert = False
                        break
                if insert:
                    executor.submit(load, item)

        # # 进程池
        # start_time_2 = time.time()
        # with ProcessPoolExecutor(max_workers=5) as executor:
        #     index = 0
        #     with open('1.txt', 'r') as fp:
        #         while True:
        #             chunk = fp.readline()
        #             if not chunk:
        #                 break
        #             index += 1
        #             executor.submit(run, index)
        # print("Process pool execution in " + str(time.time() - start_time_2), "seconds")
