# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter

# Look for duplicate items, and drop those items that were already processed
class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider):
        if item['title'] + item['author'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['title'] + item['author'])
            return item

# Export items to a JSON file
class JsonExporterPipeline(object):
    def __init__(self, file_name):
        self.file_name = file_name
        
    @classmethod
    def from_crawler(cls, crawler):
        file_name = crawler.settings.get('FILE_NAME')
        return cls(file_name)
    
    def open_spider(self, spider):
        self.file = open(self.file_name, "wb")
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()
        
    def close_spider(self, spider):
        self.exporter.finish_exporting()
        self.file.close()
    
    def process_item(self, item, spider):
        self.exporter.export_item(item)
        return item
