import os
import scrapy
from django.test import TestCase 
from UTDVN_crawler.spiders.vnu_spider import VNUSpider
from UTDVN_crawler.spiders.crawled_data_loader import CrawledDataLoader
from UTDVN_crawler import mocks
from UTDVN_crawler.pipelines import DuplicatesPipeline, JsonExporterPipeline, SolrPipeline
from UTDVN_crawler.items import Thesis
from scrapy.exceptions import DropItem
from unittest.mock import MagicMock, patch, mock_open, call

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
            self.assertRegex(item['yearpub'], '^\d{4}$')
            self.assertTrue('publisher' in item.keys())
            self.assertTrue(len(item['abstract']) > 0)
            self.assertTrue(len(item['uri']) > 0)
            self.assertTrue('file_url' in item.keys())
            self.assertEqual(item['language'], 'vi')
            self.assertTrue('keywords' in item.keys())
            
class CrawledDataLoaderTests(TestCase):
    def setUp(self):
        self.spider = CrawledDataLoader()
    
    @patch('scrapy.Request')
    def test_start_requests(self, mock_request):
        self.assertEqual(self.spider.start_requests(), [mock_request()])
        
    def test_parse(self):
        response = mocks.mock_response('/test_data/test.json')
        item_list = [item for item in self.spider.parse(response, 'thesis')]
        self.assertEqual(item_list, [{'author': 'a1', 'title': 't1'}, {'author': 'a2', 'title': 't2'}])
            
class DuplicatesPipelineTests(TestCase):
    def setUp(self):
        self.item = Thesis()
        self.item['author'] = 'a'
        self.item['title'] = 't'
        
        self.pipeline = DuplicatesPipeline()
        self.pipeline.process_item(self.item)
        
    def test_process_item_with_none_item(self):
        with self.assertRaises(TypeError):
            self.pipeline.process_item(None)
        
    def test_process_item_with_scrapy_item(self):
        with self.assertRaises(KeyError):
            self.pipeline.process_item(scrapy.Item())
        
    def test_process_item_with_no_author(self):
        item_no_author = Thesis()
        item_no_author['title'] = self.item['title']
        
        with self.assertRaises(KeyError):
            self.pipeline.process_item(item_no_author)
        
    def test_process_item_with_no_title(self):
        item_no_title = Thesis()
        item_no_title['author'] = self.item['author']
        
        with self.assertRaises(KeyError):
            self.pipeline.process_item(item_no_title)
        
    def test_process_item_with_duplicate_item(self):
        with self.assertRaises(DropItem):
            self.pipeline.process_item(self.item)
        
    def test_process_item_with_clone(self):
        item_clone = Thesis()
        item_clone['author'] = 'a'
        item_clone['title'] = 't'
        
        with self.assertRaises(DropItem):
            self.pipeline.process_item(item_clone)
        
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
        self.pipeline = JsonExporterPipeline()
        self.spider = mocks.MockSpider('test')
        
    @patch('builtins.open')
    def test_process_item(self, mock_open):
        mock_open.return_value = mock_open()
        
        item1 = Thesis()
        item1['title'] = 't1'
        item1['author'] = 'a1'
        
        item2 = Thesis()
        item2['title'] = 't2'
        item2['author'] = 'a2'
        
        self.pipeline.open_spider(self.spider)
        self.pipeline.process_item(item1, self.spider)
        self.pipeline.process_item(item2, self.spider)
        self.pipeline.close_spider(self.spider)
        
        self.assertEqual(
            mock_open().write.call_args_list, 
            [call(b'{"title": "t1", "author": "a1"}\n'), call(b'{"title": "t2", "author": "a2"}\n')])
     
class SolrPipelineTests(TestCase):
    def setUp(self):
        self.mock_solr = MagicMock()
        self.pipeline = SolrPipeline(self.mock_solr)
        
    def test_process_thesis(self):
        item = Thesis()
        item['title'] = 'some title'
        item['author'] = 'Nguyễn, Văn A'
        item['advisor'] = 'Trần, Thị B'
        item['yearpub'] = 2020
        item['publisher'] = 'tester'
        item['abstract'] = 'An example thesis.'
        item['uri'] = 'http://an.example.uri/thesis/id'
        item['file_url'] = 'http://file.url'
        item['language'] = 'ja'
        item['keywords'] = 'keyword1 , keyword2; keyword3 . keyword4  '
        
        self.pipeline.process_item(item)
        
        args = self.mock_solr.add_document.call_args[0]
        doc_type = args[0]
        doc = args[1]
        self.assertEqual(doc_type, 'thesis')
        self.assertTrue('Nguyễn_Văn_A' in doc['id'])
        self.assertTrue('some_title' in doc['id'])
        self.assertFalse(' ' in doc['id'])
        self.assertEqual(doc['type'], 'thesis')
        self.assertEqual(doc['title'], item['title'])
        self.assertEqual(doc['author'], 'Nguyễn Văn A')
        self.assertEqual(doc['description'], item['abstract'])
        self.assertRegex(doc['updatedAt'], '^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$')
        self.assertTrue(doc['yearpub'], item['yearpub'])
        self.assertTrue(doc['publisher'], item['publisher'])
        self.assertEqual(doc['advisor'], 'Trần Thị B')
        self.assertEqual(doc['uri'], item['uri'])
        self.assertTrue(doc['file_url'], item['file_url'])
        self.assertEqual(doc['language'], item['language'])
        self.assertEqual(doc['keywords'], ['keyword1', 'keyword2', 'keyword3', 'keyword4'])
        
    def test_close_spider(self):
        self.pipeline.close_spider()
        self.assertTrue(self.mock_solr.add_queued.called)
        self.assertTrue(self.mock_solr.optimize.called)