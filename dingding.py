import pymongo
import re
import csv
import datetime
import requests


def notify(title, chinese_title, category, abstract, link, page):
    print(title, chinese_title, category)

    access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwde6ec503081c8426&corpsecret=_iyW_Dv_VonG628Pqhj2ofc2lPzRvuAtKUc17yf-wZ8'
    responnse = requests.get(url=access_token_url)
    if responnse.ok and responnse.json()['errcode'] == 0:
        access_token = responnse.json()['access_token']
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        # data = {
        #     "touser": "HuangXinPing",
        #     "msgtype": "markdown",
        #     "agentid": "1000004",
        #     "markdown": {
        #         "content": f"""您今天的论文已准备好`
        #         >**论文详情**
        #         >类   别：<font color=\"info\">{category}</font>
        #         >原始标题：<font color=\"warning\">{title}</font>
        #         >标   题：<font color=\"comment\">{chinese_title}</font>"""
        #     }
        # }

        # 1. 发送基本信息
        data = {
            "touser": "HuangXinPing",
            "msgtype": "text",
            "agentid": "1000004",
            "text": {
                "content": f"{category}\n\n{title}\n\n{chinese_title}\n\n{page}\n\n{link}"
            }
        }
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        requests.post(url=url, json=data, headers=headers)

        # 2. 发送简介，以便微信上方便翻译 - 佩服我自己。。。
        data = {
            "touser": "HuangXinPing",
            "msgtype": "text",
            "agentid": "1000004",
            "text": {
                "content": f"{abstract}"
            }
        }
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
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
    date_regx = re.compile(datetime.datetime.now().strftime('%Y-%m-%d'), re.IGNORECASE)
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
        notify(doc['title'], doc['chinese_title'], translates[doc['subjects'][0]['short']], doc['abstract'], doc['url'], doc['attachment'])


if __name__ == '__main__':
    main()
