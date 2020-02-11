# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
from UTDVN_database.solr import connection

# Looks for duplicate items, and drop those items that were already processed
class DuplicatesPipeline(object):
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider):
        if item['author'] + '_' + item['title'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['author'] + '_' + item['title'])
            return item

# Exports items to a JSON file
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
    
# Stores items in Solr
class SolrPipeline(object):
    def __init__(self):
        self.solr_items = []
        
    def close_spider(self, spider):
        connection.add_items(self.solr_items)
    
    def process_item(self, item, spider):
        solr_item = dict(item)
        solr_item['author'] = solr_item['author'].replace(',', '')
        solr_item['advisor'] = solr_item['advisor'].replace(',', '')
        solr_item['id'] = solr_item['author'] + '_' + solr_item['title']
        self.solr_items.append(solr_item)
        return item
