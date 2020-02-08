# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy

class Thesis(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    advisor = scrapy.Field()
    publish_date = scrapy.Field()
    publisher = scrapy.Field()
    abstract = scrapy.Field()
    uri = scrapy.Field()
    file_url = scrapy.Field()
    language = scrapy.Field()
    keywords = scrapy.Field()
