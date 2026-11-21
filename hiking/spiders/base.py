from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider

from hiking.items import TrailItem

class BaseTrailSpider(CrawlSpider):
    """Shared parsing."""

    selectors = {} # field name -> CSS selector, filled in by each site

    def parse_trails(self, response): # self = instance method
        loader = ItemLoader(item=TrailItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("source", self.name)

        for field, css in self.selectors.items():
            # e.g., loaader.add_css("name", "h1::text")
            loader.add_css(field, css)

        yield loader.load_item()