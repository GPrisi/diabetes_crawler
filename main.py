from feapder import ArgumentParser
import feapder
from spiders import *

 
 
def crawl_list():
    """
    列表爬虫
    """
    spider = list_spider.ListSpider(redis_key="feapder:crawl_diabetes")
    # 调试：spider = list_spider.ListSpider.to_DebugSpider(
    #                                                     redis_key="feapder:crawl_diabetes",
    #                                                     request=feapder.Request("https://diabetestalk.net")
    #                                                     )
    
    spider.start()
 
 
def crawl_detail(args):
    """
    详情爬虫
    @param args: 1 / 2 / init
    """
    spider = categ_spider.CategSpider( #).to_DebugBatchSpider(
        #task_id=1,
        redis_key="feapder:crawl_diabetes",  # redis中存放任务等信息的根key
        task_table="blog_theme",  # mysql中的任务表
        task_keys=["id", "url"],  # 需要获取任务表里的字段名，可添加多个
        task_state="state",  # mysql中任务状态字段
        batch_record_table="crawl_diabetes_batch_record",  # mysql中的批次记录表
        batch_name="crawl_diabetes",  # 批次名字
        batch_interval=4,  # 批次周期 天为单位 若为小时 可写 1 / 24
    )
 
    if args == 1:
        spider.start_monitor_task()
    elif args == 2:
        spider.init_task() #调试
        spider.start()
 
 
if __name__ == "__main__":
    parser = ArgumentParser(description="lsp爬虫")
 
    parser.add_argument(
        "--crawl_list", action="store_true", help="列表爬虫", function=crawl_list
    )
    parser.add_argument(
        "--crawl_detail", type=int, nargs=1, help="详情爬虫(1|2）", function=crawl_detail
    )
 
    parser.start()


    