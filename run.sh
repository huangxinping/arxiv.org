#!/usr/bin/env bash
#rm -rf output.json
#rm -rf output.log
#rm -rf crawls
#rm -rf .scrapy

#-o output.json  输出结果
#-s LOG_FILE=output.log  运行log
#-s JOBDIR=crawls/robot  运行缓存
#-s CLOSESPIDER_ITEMCOUNT=90 运行限制
#-s CLOSESPIDER_PAGECOUNT=10 运行限制
#-s CLOSESPIDER_TIMEOUT=10 运行限制

#scrapy crawl arxiv -o output.json -s JOBDIR=crawls/robot -s HTTPCACHE_ENABLED=0
scrapy crawl arxiv -s JOBDIR=crawls/robot -s HTTPCACHE_ENABLED=1
