from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == "__main__":
    process = CrawlerProcess(get_project_settings())
    process.crawl('crawled_data_loader')
    process.start()