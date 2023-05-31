import pymongo
import re
import csv
import datetime
import requests
from translate import translate_with_baidu

current_access_token = None


def notify_dingding(title, chinese_title, category, abstract, page, paper, created_at):
    """
    References: https://www.cnblogs.com/tjp40922/p/11299023.html
    """
    chinese_abstract = translate_with_baidu(abstract)
    url = 'https://oapi.dingtalk.com/robot/send?access_token=cb57e398c71b1f447fc6c2972187809776231f9067cc8cd68d011322848f7559'
    # data = {
    #     "msgtype": "markdown",
    #     "markdown": {
    #         "title": chinese_title,
    #         "text": "#### " + chinese_abstract + "\n" +
    #                 "> ###### 类别: " + category + "\n" +
    #                 "> ###### 发表时间: " + created_at + "\n" +
    #                 "> ###### 论文地址: " + paper + "\n"
    #     }
    # }
    data = {
        "actionCard": {
            "title": chinese_title,
            "text": "# "+ chinese_title + "\n" +
                    "`"+ category + "`" + " `" + created_at + "`" + "\n" +
                    "###### " + chinese_abstract,
            "hideAvatar": "0",
            "btnOrientation": "0",
            "singleTitle": "阅读全文",
            "singleURL": paper,
        },
        "msgtype": "actionCard"
    }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    responnse = requests.post(url=url, json=data, headers=headers)
    responnse.encoding = 'utf-8'
    if responnse.status_code == 200:
        print(responnse.json())


def notify_weixin(title, chinese_title, category, abstract, page, paper, created_at):
    """
    docs: https://work.weixin.qq.com/api/doc/90001/90143/90372#%E6%96%87%E6%9C%AC%E5%8D%A1%E7%89%87%E6%B6%88%E6%81%AF
    """

    def send(access_token, title, chinese_title, category, abstract, page, paper, created_at):
        if len(chinese_title) <= 0:
            chinese_title = title
        url = f'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token={access_token}'
        chinese_abstract = translate_with_baidu(abstract)
        headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
        data = {
            "touser": "HuangXinPing|jiny",
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

    client = pymongo.MongoClient("192.168.0.23", 21017)
    subject_regx = re.compile("^cs.", re.IGNORECASE)
    today = datetime.datetime.now()
    for offset in range(30):
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
        print(keeped_docs)
        for doc in keeped_docs:
            if doc.get('notified', False):
                continue

            category = ''
            for item in doc['subjects']:
                if str(item['short']).startswith('cs.'):
                    category = item['short']
                    break

            # notify_weixin(doc['title'], doc['chinese_title'], translates[category], doc['abstract'], doc['url'],
            #        doc['attachment'], date.strftime('%Y-%m-%d'))
            notify_dingding(doc['title'], doc['chinese_title'], translates[category], doc['abstract'], doc['url'],
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
