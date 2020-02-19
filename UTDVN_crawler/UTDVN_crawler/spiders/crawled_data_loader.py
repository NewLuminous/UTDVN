# -*- coding: utf-8 -*-
import scrapy
from UTDVN_crawler.items import Thesis
import json, os

import logging

class CrawledDataLoader(scrapy.Spider):
    name = 'crawled_data_loader'
    
    def start_requests(self):
        crawled_data_dir = "file:////" + os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + "/crawled_data/"
        vnu_request = scrapy.Request(url=crawled_data_dir + "vnu.json",cb_kwargs=dict(item_type='thesis'))
        return [vnu_request]
    
    def parse(self, response, item_type):
        item_list = [json.loads(item) for item in response.text.split('\n') if item != '']
        for item in item_list:
            if item_type == 'thesis':
                thesis = Thesis()
            for key in item.keys():
                thesis[key] = item[key]
            
            yield thesis