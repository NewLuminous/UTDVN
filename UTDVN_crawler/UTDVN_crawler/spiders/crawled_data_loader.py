# -*- coding: utf-8 -*-
import scrapy
from UTDVN_crawler.items import Thesis
import json

class CrawledDataLoader(scrapy.Spider):
    name = 'crawled_data_loader'
    start_urls = ["file:///home/utdvn/UTDVN_crawler/UTDVN_crawler/crawled_data/vnu.json"]
    
    def parse(self, response):
        item_list = [json.loads(item) for item in response.text.split('\n') if item != '']
        for item in item_list:
            thesis = Thesis()
            for key in item.keys():
                thesis[key] = item[key]
            
            yield thesis