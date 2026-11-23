from hiking.items import TrailItem
from hiking.spiders.base import BaseTrailSpider
import scrapy
from scrapy.loader import ItemLoader

# Spider: class that says where to start and how to parse each response
class TrailsSpider(scrapy.Spider):
    """Crawl the trail search results on myswitzerland.com and extract each trail's details.
    In myswitzerland.com, the search results are paginated, and each trail has a detail page 
    with a table of properties (start, end, difficulty, fitness, etc.) and a description."""
    
    name = "trails"
    allowed_domains = ["www.myswitzerland.com"] # stops the crawl from leaving the website 
    start_urls = ["https://www.myswitzerland.com/en-ch/experiences/summer-autumn/hiking/hiking-search/"]

    custom_settings = {
        "DOWNLOAD_DELAY": 1,
        "USER_AGENT": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/158.0.0.0 Safari/537.36"
    }

    def parse(self, response):
        """Follow every trail link, then the next page."""

        for href in response.css("a.OfferTeaser--link::attr(href)").getall():
            yield response.follow(href, callback=self.parse_trail) # 'yield' returns the result and continues to the next step

        next_page = response.css("a.Pagination--link.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse) # Queues another page to crawl

    def parse_trail(self, response):
        """Detail page: extract one record."""
        loader = ItemLoader(item=TrailItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("source", self.name)
        loader.add_value("name", response.css("h1.PageHeader--title::text").get())
        loader.add_value("start", response.xpath("//th[normalize-space()='Start location']/following-sibling::td/div[@class='richtext']/text()").get())
        loader.add_value("end", response.xpath("//th[normalize-space()='Destination']/following-sibling::td/div[@class='richtext']/text()").get())
        loader.add_value("difficulty", response.xpath("//th[normalize-space()='Technical requirements']/following-sibling::td/div[@class='richtext']/text()").get())
        loader.add_value("fitness", response.xpath("//th[normalize-space()='Physical requirements']/following-sibling::td/div[@class='richtext']/text()").get())
        loader.add_value("description", response.xpath("//div[@class='ArticleSection--title' and text()='Description']//div[@class='richtext']//text()").getall())

        yield loader.load_item()