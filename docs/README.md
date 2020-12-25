- 各类别 XPath 提取子

> 提取 Mathematics 

```
url: https://arxiv.org/
XPath: //ul/li/a[starts-with(@id,'math')]/@id
```

> 提取 Computer Science

```
url: https://arxiv.org/
XPath: //ul/li/a[starts-with(@id,'cs')]/@id
```

> 提取 Quantitative Biology

```
url: https://arxiv.org/
XPath: //ul/li/a[starts-with(@id,'q-bio')]/@id
```

- 提取总数

```
url: https://arxiv.org/list/cs.LG/recent
XPath: //div[@id="dlpage"]/h3
regex: of \d{1,} and replace('of ', '')
```

- 提取列表

```
url: https://arxiv.org/list/cs.LG/pastweek?skip=0&show=93
XPath: //span[@class='list-identifier']/a[@title='Abstract']/@href
```

- 提取细节

```
url: https://arxiv.org/abs/2012.12206
XPath:
    - title: //h1[@class='title mathjax']
    - authors: //div[@class='authors']/a/text()
    - authors link: //div[@class='authors']/a/@href
```