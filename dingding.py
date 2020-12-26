import pymongo
import re
import csv
import datetime
import requests
import time
import hashlib
import http.client
import urllib
import random
import json


def baidu_translate(text):
    appid = '20201116000617930'  # 填写你的appid
    secretKey = 'PSrK_o403EnySZ_SvIXn'  # 填写你的密钥

    httpClient = None
    myurl = '/api/trans/vip/translate'

    fromLang = 'auto'  # 原文语种
    toLang = 'zh'  # 译文语种
    salt = random.randint(32768, 65536)
    q = text
    sign = appid + q + str(salt) + secretKey
    sign = hashlib.md5(sign.encode()).hexdigest()
    myurl = myurl + '?appid=' + appid + '&q=' + urllib.parse.quote(
        q) + '&from=' + fromLang + '&to=' + toLang + '&salt=' + str(
        salt) + '&sign=' + sign

    try:
        httpClient = http.client.HTTPConnection('api.fanyi.baidu.com')
        httpClient.request('GET', myurl)

        # response是HTTPResponse对象
        response = httpClient.getresponse()
        result_all = response.read().decode("utf-8")
        result = json.loads(result_all)

        print(result)
        if 'error_code' not in result:
            return result['trans_result'][0]['dst']
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
    return text


def notify(title, chinese_title, category, abstract, page, paper, created_at):
    print(category, chinese_title, created_at)

    """
    docs: https://work.weixin.qq.com/api/doc/90001/90143/90372#%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF
    """
    access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwde6ec503081c8426&corpsecret=_iyW_Dv_VonG628Pqhj2ofc2lPzRvuAtKUc17yf-wZ8'
    response = requests.get(url=access_token_url)
    if response.ok and response.json()['errcode'] == 0:
        access_token = response.json()['access_token']
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        chinese_abstract = baidu_translate(abstract)
        data = {
            "touser": "HuangXinPing",
            "msgtype": "textcard",
            "agentid": "1000004",
            "textcard": {
                "title": f"{chinese_title}",
                "description": f"<div class=\"gray\">{created_at} {category}</div> <div class=\"normal\">点击查看论文<br><br>⏬⏬⏬⏬⏬论文简介⏬⏬⏬⏬⏬⏬</div>",
                "url": f"{paper}",
                "btntxt": "更多"
            },
        }
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        requests.post(url=url, json=data, headers=headers)

        data = {
            "touser": "HuangXinPing|LiuTao|jiny",
            "msgtype": "text",
            "agentid": "1000004",
            "text": {
                "content": f"{chinese_abstract}"
            }
        }
        requests.post(url=url, json=data, headers=headers)


def main():
    translates = {}
    with open('docs/Computer Science.csv') as r:
        spamreader = csv.reader(r, delimiter=',')
        header = next(spamreader)
        for row in spamreader:
            translates[row[0]] = row[2]

    client = pymongo.MongoClient("192.168.0.210", 27017)
    subject_regx = re.compile("^cs.", re.IGNORECASE)
    today = datetime.datetime.now().strftime('%Y-%m-%d')
    yesterday = (datetime.datetime.now() - datetime.timedelta(1)).strftime('%Y-%m-%d')
    date_regx = re.compile(yesterday, re.IGNORECASE)
    cursor = client.papers.arxiv.find({
        'submissions.date': date_regx,
        'subjects.short': subject_regx
    })

    keeped_titles = []
    keeped_docs = []
    for doc in cursor:
        if doc['title'] not in keeped_titles:
            keeped_titles.append(doc['title'])
            keeped_docs.append(doc)
    for doc in keeped_docs:
        notify(doc['title'], doc['chinese_title'], translates[doc['subjects'][0]['short']], doc['abstract'], doc['url'], doc['attachment'], yesterday)


if __name__ == '__main__':
    main()
