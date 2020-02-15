# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import datetime
from scrapy.exceptions import DropItem
from scrapy.exporters import JsonLinesItemExporter
from .items import Thesis
from UTDVN_database.views import SOLR
from UTDVN_database.solr.models import *

class DuplicatesPipeline(object):
    """
    Looks for duplicate items, and drop those items that were already processed
    """
    
    def __init__(self):
        self.ids_seen = set()
        
    def process_item(self, item, spider=None):
        if item['author'] + '_' + item['title'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['author'] + '_' + item['title'])
            return item

class JsonExporterPipeline(object):
    """
    Exports items to a JSON file
    """
    
    def __init__(self, file_name):
        self.file_name = file_name
        
    @classmethod
    def from_crawler(cls, crawler):
        file_name = crawler.settings.get('FILE_NAME')
        return cls(file_name)
    
    def open_spider(self, spider=None):
        self.file = open(self.file_name, "wb")
        self.exporter = JsonLinesItemExporter(self.file)
        self.exporter.start_exporting()
        
    def close_spider(self, spider=None):
        self.exporter.finish_exporting()
        self.file.close()
    
    def process_item(self, item, spider=None):
        self.exporter.export_item(item)
        return item
    
class SolrPipeline(object):
    """
    Stores items in Solr
    """
    
    def __init__(self, solr_connection=SOLR):
        self.solr_connection = solr_connection
        
    def close_spider(self, spider=None):
        """
        Defragments Solr when spider closed.
        """
        print('Emptying all queued documents')
        self.solr_connection.add_queued()
        print('Optimizing all Solr cores')
        self.solr_connection.optimize()
    
    def process_item(self, item, spider=None):
        if isinstance(item, Thesis):
            self._process_thesis(item)
        return item
    
    def _process_thesis(self, item):
        """
        Converts Thesis item to SolrThesis and commits it to Solr.
        """
        solr_doc = SolrThesis(
            id=item['author'].replace(',', '') + '_' + item['title'],
            type='thesis',
            title=item['title'],
            author=item['author'].replace(',', ''),
            description=item['abstract'],
            updatedAt=self._get_time(),
            yearpub=item['yearpub'],
            advisor=item['advisor'].replace(',', ''),
            publisher=item['publisher'],
            uri=item['uri'],
            file_url=item['file_url'],
            language=item['language'],
            keywords=[kw.strip() for kw in item['keywords'].replace(';',',').replace('.',',').split(',')],
        )
        solr_doc.add_to_solr(self.solr_connection)
        
    def _get_time(self):
        """
        Make a UTC date string in format 'Y-m-d H:M:S'
        """
        style = '%Y-%m-%d %H:%M:%S'
        return datetime.datetime.now().strftime(style)