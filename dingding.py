import pymongo
import re
import csv
import datetime
import requests
from translate import translate_with_baidu

current_access_token = None


def notify(title, chinese_title, category, abstract, page, paper, created_at):
    """
    docs: https://work.weixin.qq.com/api/doc/90001/90143/90372#%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF
    """

    def send(access_token, title, chinese_title, category, abstract, page, paper, created_at):
        if len(chinese_title) <= 0:
            return
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        chinese_abstract = translate_with_baidu(abstract)
        data = {
            "touser": "HuangXinPing|LiuTao|jiny|PuPu" if category == '图形' or category == '人机交互' else "HuangXinPing|LiuTao|jiny",
            # "touser": "HuangXinPing",
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
            "touser": "HuangXinPing|LiuTao|jiny|PuPu" if category == '图形' or category == '人机交互' else "HuangXinPing|LiuTao|jiny",
            # "touser": "HuangXinPing",
            "msgtype": "text",
            "agentid": "1000004",
            "text": {
                "content": f"{chinese_abstract}"
            }
        }
        requests.post(url=url, json=data, headers=headers)

    if current_access_token:
        access_token = current_access_token
        send(access_token, title, chinese_title, category, abstract, page, paper, created_at)
    else:
        access_token_url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken?corpid=wwde6ec503081c8426&corpsecret=_iyW_Dv_VonG628Pqhj2ofc2lPzRvuAtKUc17yf-wZ8'
        response = requests.get(url=access_token_url)
        if response.ok and response.json()['errcode'] == 0:
            access_token = response.json()['access_token']
            send(access_token, title, chinese_title, category, abstract, page, paper, created_at)


def main():
    translates = {}
    with open('docs/Computer Science.csv') as r:
        spamreader = csv.reader(r, delimiter=',')
        header = next(spamreader)
        for row in spamreader:
            translates[row[0]] = row[2]

    client = pymongo.MongoClient("192.168.0.210", 27017)
    subject_regx = re.compile("^cs.", re.IGNORECASE)
    today = datetime.datetime.now()
    for offset in range(0, 5):
        date = today - datetime.timedelta(offset)
        cursor = client.papers.arxiv.find({
            'submissions.date': date.strftime('%Y-%m-%d'),
            'subjects.short': subject_regx
        })

        keeped_titles = []
        keeped_docs = []
        for doc in cursor:
            if doc['title'] not in keeped_titles:
                keeped_titles.append(doc['title'])
                keeped_docs.append(doc)
        for doc in keeped_docs:
            if doc.get('notified', False):
                continue

            category = ''
            for item in doc['subjects']:
                if str(item['short']).startswith('cs.'):
                    category = item['short']
                    break

            notify(doc['title'], doc['chinese_title'], translates[category], doc['abstract'], doc['url'],
                   doc['attachment'], date.strftime('%Y-%m-%d'))

            client.papers.arxiv.update_one({
                'title': doc['title']
            }, {
                '$set': {
                    'notified': True
                }
            }, upsert=False)


if __name__ == '__main__':
    main()
