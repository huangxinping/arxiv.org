FROM python:3.6.0-slim
LABEL author="huangxinping<o0402@outlook.com>"

ENV TIME_ZONE=Asia/Shanghai
RUN echo "${TIME_ZONE}" > /etc/timezone \
    && ln -sf /usr/share/zoneinfo/${TIME_ZONE} /etc/localtime

RUN mkdir /src
COPY . /src
WORKDIR /src

RUN pip install -r requirements.txt
#RUN pip install -r requirements.txt -i https://pypi.doubanio.com/simple/ --trusted-host pypi.doubanio.com

RUN find . -name "*.pyc" -delete

CMD ["scrapy", "crawl", "arxiv"]