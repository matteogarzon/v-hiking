from hiking.items import TrailItem
from hiking.spiders.base import BaseTrailSpider
import scrapy
from scrapy.loader import ItemLoader

# Spider: class that says where to start and how to parse each response
class TrailsSpider(BaseTrailSpider):
    name = "trails"
    allowed_domains = ["www.myswitzerland.com"] # stops the crawl from leaving the website 
    start_urls = ["https://www.myswitzerland.com/en-ch/experiences/summer-autumn/hiking/hiking-search/"]

    def parse(self, response):
        """Follow every trail link, then the next page."""

        for href in response.css("a.OfferTeaser--link::attr(href)").getall():
            yield response.follow(href, callback=self.parse_trail) # yield returns the result and continues to the next step

        next_page = response.css("a.Pagination--link.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse) #queues another page to crawl

    def parse_trail(self, response):
        """Detail page: extract one record."""
        loader = ItemLoader(item=TrailItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("source", self.name)
        loader.add_value("start", response.xpath("//th[normalize-space(text())='Start Location']//following-sibling::td/text()").get())
        loader.add_value("end", response.xpath("//th[normalize-space(text())='Destination']//following-sibling::td/text()").get())
        loader.add_value("difficulty", response.xpath("//th[normalize-space(text())='Technical requirements']//following-sibling::td/text()").get())
        loader.add_value("fitness", response.xpath("//th[normalize-space(text())='Physical requirements']//following-sibling::td/text()").get())
        loader.add_value("description", response.xpath("//div[@class='ArticleSection--title' and text()='Description']//following-sibling::div[@class='richtext']//text()").getall())

        yield loader.load_item()