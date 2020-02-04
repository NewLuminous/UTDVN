# -*- coding: utf-8 -*-
import scrapy
from UTDVN_crawler.items import Thesis

class VNUSpider(scrapy.Spider):
    name = "vnu"
    allowed_domains = ['repository.vnu.edu.vn']
    start_urls = [
        'https://repository.vnu.edu.vn/community-list',
    ]
            
    def parse(self, response):
        # follow links to member units' undergraduate theses
        for a in response.css('.media-heading').xpath('a[re:test(text(),".*Undergraduate Theses$")]'):
            yield response.follow(a, callback=self.parse_member_unit)
            
    def parse_member_unit(self, response):
        # follow pagination links
        for offset in response.css('a#offset::attr(name)').getall():
            yield scrapy.Request(response.url + '?offset=%s' % offset, callback=self.parse_member_unit_offset)
            
    def parse_member_unit_offset(self, response):
        # follow links to thesis pages
        for a in response.xpath('//div[re:test(@class,".*browse-titles$")]//a'):
            yield response.follow(a, callback=self.parse_thesis)
            
    def parse_thesis(self, response):
        # follow links to detail page
        yield scrapy.Request(response.url + '?mode=full', callback=self.parse_thesis_metadata)

    def parse_thesis_metadata(self, response):        
        def extract_meta(name):
            return response.xpath('//meta[re:test(@name,".*%s$")]/@content' % name).get(default='').strip()
        
        item = Thesis()
        item['title'] = extract_meta('title')
        item['author'] = extract_meta('creator')
        item['advisor'] = extract_meta('contributor')
        item['publish_date'] = extract_meta('citation_date')
        item['publisher'] = extract_meta('publisher')
        item['abstract'] = extract_meta('abstract')
        item['uri'] = extract_meta('identifier')
        item['file_url'] = extract_meta('pdf_url')
        item['language'] = extract_meta('language')
        item['keywords'] = extract_meta('keywords')
        yield item