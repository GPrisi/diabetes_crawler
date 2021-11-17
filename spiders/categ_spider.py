# -*- coding: utf-8 -*-
"""
Created on 2021-09-16 17:33:11
---------
@summary:
---------
@author: root
"""

import feapder
from fake_useragent import UserAgent
from feapder.network.selector import Selector
import random
import re
from items import *


class CategSpider(feapder.BatchSpider):
    def start_requests(self, task):
        task_id, url = task
        yield feapder.Request(url, task_id=task_id)

    def download_midware(self, request):
        # 随机UA
        request.headers = {'User-Agent': str(UserAgent(path="./fakeuseragent.json").random)}
        return request

    def parse(self, request, response):
        for a_tag in response.bs4().select('ul li a'):
            href = str(a_tag.get('href'))
            # title = str(a_tag.get('title'))
            href_tail = re.findall('(?<=https://diabetestalk.net/).*$', href)[0] #获取https://diabetestalk.net后面的内容
            regex = re.compile(r'^[^(aboutus|contactus|privacy|terms)]')    #排除aboutus等无效页面 
            if re.search(regex,href_tail) and ('/' in href_tail): #排除类别页面，只爬取博客页面
                if "popular/" not in href_tail :   #热门文章没有分类
                    blog_item = dbt_talk_blog_item.DbtTalkBlogItem()
                    blog_item.theme_id = request.task_id #todo
                    blog_item.url = href
                    blog_item.title = href_tail.split('/')[1]
                    yield blog_item
     
                    # 再次下发新任务，爬博客内容页面 #并带上
                    yield feapder.Request(href, download_midware=self.download_midware, 
                                            callback=self.parse_blog_page)
        yield self.update_task_batch(request.task_id, 1)  # 更新任务状态


    def parse_blog_page(self, request, response):
        selector = Selector(response.text)
        title = selector.xpath("//*[@id=\"post-header\"]/div/div/h1/text()").extract_first()
        
        for out_site in response.bs4().select('p a'):
            exlink_item = external_link_item.ExternalLinkItem()
            exlink_item.content = out_site.find_parent()
            exlink_item.url = out_site.get('href')
            exlink_item.title = out_site.find_parent().find_previous_sibling('h2').get_text()
            exlink_item.blog_url = request.url
            yield exlink_item
        
        # update_time = selector.xpath("//*[@id=\"post-header\"]/div/div/div[1]/ol/li[3]/span/time//@datetime").extract_first()




if __name__ == "__main__":
    spider = CategSpider(
        redis_key="feapder:crawl_diabetes",  # redis中存放任务等信息的根key
        task_table="blog_theme",  # mysql中的任务表
        task_keys=["id", "url"],  # 需要获取任务表里的字段名，可添加多个
        task_state="state",  # mysql中任务状态字段
        batch_record_table="crawl_diabetes_batch_record",  # mysql中的批次记录表
        batch_name="crawl_diabetes",  # 批次名字
        batch_interval=4,  # 批次周期 天为单位 若为小时 可写 1 / 24
    )

    # spider.start_monitor_task() # 下发及监控任务
    spider.start() # 采集
