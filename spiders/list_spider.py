# -*- coding: utf-8 -*-
"""
Created on 2021-09-15 23:20:41
---------
@summary:
---------
@author: root
"""

# from feapder.network.selector import Selector

import feapder
from fake_useragent import UserAgent
import random
import re
from items import *

class ListSpider(feapder.Spider):

    def start_requests(self):
        yield feapder.Request("https://diabetestalk.net")

    def download_midware(self, request):
        # 随机UA
        request.headers = {'User-Agent': str(UserAgent(path="./fakeuseragent.json").random)}
        return request

    def parse(self, request, response):
        for a_tag in response.bs4().find_all("a",href=re.compile(r'^(https://diabetestalk.net/((?!(aboutus|contactus|privacy|terms)).)*$)')): 
            url = a_tag.get('href')
            #title = a_tag.get('title')
            
            # 分开文章页面和类别页面 :字符串“https://diabetestalk.net/”后面是否还存在符号“/”
            url_tail = re.findall('(?<=https://diabetestalk.net/).*$', url)[0]
            if '/' in url_tail:  # 文章页面 #可以删掉
                blog_item = dbt_talk_blog_item.DbtTalkBlogItem()
                blog_item.url = url
                yield blog_item  # 直接返回，框架实现批量入库
            else :  # 类别页面 
                theme_item = blog_theme_item.BlogThemeItem()
                theme_item.url = url            
                theme_item.name = url_tail
                yield theme_item  # 自动批量入库

            

if __name__ == "__main__":
    spider = ListSpider.to_DebugSpider(redis_key="feapder:crawl_diabetes")
    spider.start()
