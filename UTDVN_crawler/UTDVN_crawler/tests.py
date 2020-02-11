import os
import scrapy
from django.test import TestCase 
from UTDVN_crawler.spiders.vnu_spider import VNUSpider
from UTDVN_crawler import mocks
from UTDVN_crawler.pipelines import *
from UTDVN_crawler.items import Thesis
from scrapy.exceptions import DropItem
from unittest.mock import MagicMock
from UTDVN_database.solr import connection

class VNUSpiderTests(TestCase):
    def setUp(self):
        self.spider = VNUSpider()
    
    def test_parse(self):
        response = mocks.mock_response('/test_data/community-list.html')
        for follow_request in self.spider.parse(response):
            self.assertRegex(follow_request.url, '^https:\/\/repository.vnu.edu.vn\/handle\/VNU_123\/\d+$')
            
    def test_parse_member_unit(self):
        response = mocks.mock_response('/test_data/33317.html', 'https://repository.vnu.edu.vn/handle/VNU_123/33317')
        for request in self.spider.parse_member_unit(response):
            self.assertRegex(request.url, '^https:\/\/repository.vnu.edu.vn\/handle\/VNU_123\/\d+\?offset=\d+$')
            
    def test_parse_member_unit_offset(self):
        response = mocks.mock_response('/test_data/33317.html', 'https://repository.vnu.edu.vn/handle/VNU_123/33317?offset=0')
        for follow_request in self.spider.parse_member_unit_offset(response):
            self.assertRegex(follow_request.url, '^https:\/\/repository.vnu.edu.vn\/handle\/VNU_123\/\d+$')
            
    def test_parse_thesis(self):
        response = mocks.mock_response('/test_data/63050.html', 'https://repository.vnu.edu.vn/handle/VNU_123/63050')
        for request in self.spider.parse_thesis(response):
            self.assertRegex(request.url, '^https:\/\/repository.vnu.edu.vn\/handle\/VNU_123\/\d+\?mode=full$')
            
    def test_parse_thesis_metadata(self):
        response = mocks.mock_response('/test_data/63050_mode=full.html', 'https://repository.vnu.edu.vn/handle/VNU_123/63050?mode=full')
        for item in self.spider.parse_thesis_metadata(response):
            self.assertTrue(len(item['title']) > 0)
            self.assertTrue(len(item['author']) > 0)
            self.assertTrue('advisor' in item.keys())
            self.assertTrue(len(item['publish_date']) > 0)
            self.assertTrue('publisher' in item.keys())
            self.assertTrue(len(item['abstract']) > 0)
            self.assertTrue(len(item['uri']) > 0)
            self.assertTrue('file_url' in item.keys())
            self.assertEqual(item['language'], 'vi')
            self.assertTrue('keywords' in item.keys())
            
class DuplicatesPipelineTests(TestCase):
    def setUp(self):
        self.item = Thesis()
        self.item['author'] = 'a'
        self.item['title'] = 't'
        
        self.pipeline = DuplicatesPipeline()
        self.pipeline.process_item(self.item)
        
    def test_process_item_with_none_item(self):
        self.assertRaises(TypeError, self.pipeline.process_item, None)
        
    def test_process_item_with_scrapy_item(self):
        self.assertRaises(KeyError, self.pipeline.process_item, scrapy.Item())
        
    def test_process_item_with_no_author(self):
        item_no_author = Thesis()
        item_no_author['title'] = self.item['title']
        
        self.assertRaises(KeyError, self.pipeline.process_item, item_no_author)
        
    def test_process_item_with_no_title(self):
        item_no_title = Thesis()
        item_no_title['author'] = self.item['author']
        
        self.assertRaises(KeyError, self.pipeline.process_item, item_no_title)
        
    def test_process_item_with_duplicate_item(self):
        self.assertRaises(DropItem, self.pipeline.process_item, self.item)
        
    def test_process_item_with_clone(self):
        item_clone = Thesis()
        item_clone['author'] = 'a'
        item_clone['title'] = 't'
        
        self.assertRaises(DropItem, self.pipeline.process_item, item_clone)
        
    def test_process_item_with_same_author(self):
        item_same_author = Thesis()
        item_same_author['author'] = self.item['author']
        item_same_author['title'] = self.item['title'] + self.item['title']
        
        self.assertEqual(self.pipeline.process_item(item_same_author), item_same_author)
        
    def test_process_item_with_same_title(self):
        item_same_title = Thesis()
        item_same_title['author'] = self.item['author'] + self.item['author']
        item_same_title['title'] = self.item['title']
        
        self.assertEqual(self.pipeline.process_item(item_same_title), item_same_title)
        
    def test_process_item_with_similar_item_with_empty_author(self):
        similar_item = Thesis()
        similar_item['author'] = ''
        similar_item['title'] = self.item['author'] + self.item['title']
        
        self.assertEqual(self.pipeline.process_item(similar_item), similar_item)
        
    def test_process_item_with_similar_item_with_empty_title(self):
        similar_item = Thesis()
        similar_item['author'] = self.item['author'] + self.item['title']
        similar_item['title'] = ''
        
        self.assertEqual(self.pipeline.process_item(similar_item), similar_item)
        
    def test_process_item_with_different_item(self):
        different_item = Thesis()
        different_item['author'] = self.item['title']
        different_item['title'] = self.item['author']
        
        self.assertEqual(self.pipeline.process_item(different_item), different_item)
        
class JsonExporterPipelineTests(TestCase):
    def setUp(self):
        self.file_name = 'test.json'
        self.pipeline = JsonExporterPipeline(self.file_name)
        
    def tearDown(self):
        os.remove(self.file_name)
        
    def test_process_item(self):
        item1 = Thesis()
        item1['title'] = 't1'
        item1['author'] = 'a1'
        
        item2 = Thesis()
        item2['title'] = 't2'
        item2['author'] = 'a2'
        
        self.pipeline.open_spider()
        self.pipeline.process_item(item1)
        self.pipeline.process_item(item2)
        self.pipeline.close_spider()
        
        file_content = open(self.file_name, 'r').read()
        self.assertEqual(file_content, '{"title": "t1", "author": "a1"}\n{"title": "t2", "author": "a2"}\n')
        
class SolrPipelineTests(TestCase):
    def setUp(self):
        self.pipeline = SolrPipeline()
        self.connection_add_items = connection.add_items
        connection.add_items = MagicMock()
        
    def tearDown(self):
        connection_add_items = self.connection_add_items
        
    def test_process_item(self):
        item = Thesis()
        item['title'] = 't'
        item['author'] = 'Nguyễn, Văn A'
        item['advisor'] = 'Trần, Thị B'
        self.pipeline.process_item(item)
        self.pipeline.close_spider()
        
        args = connection.add_items.call_args[0][0][0]
        self.assertEqual(args['title'], 't')
        self.assertEqual(args['author'], 'Nguyễn Văn A')
        self.assertEqual(args['advisor'], 'Trần Thị B')
        self.assertTrue(args['title'] in args['id'])
        self.assertTrue(args['author'] in args['id'])