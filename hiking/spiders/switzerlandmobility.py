import scrapy
from scrapy.loader import ItemLoader

from hiking.items import TrailItem
from hiking.spiders.base import BaseTrailSpider

# plain JSON spider
class SwitzerlandMobility(BaseTrailSpider):
    name = "switzerlandmobility"
    allowed_domains = ["schweizmobil.ch"]
    API = "https://schweizmobil.ch/api/4/routes/hike/{category}?lang=en"

    #  replacement for start_urls and start_requests() since we want to build the URLs ourselves
    async def start(self):
        for category in ["national", "regional", "local"]:
            yield scrapy.Request(self.API.format(category=category), callback=self.parse)

    # Use add_value instead of add_css (where Scrapy extracts the value from the response using a CSS selector)
    def parse(self, response):
        for route in response.json():               # a list of route dicts
            loader = ItemLoader(item=TrailItem())   # no response=, because there is no HTML to select from
            loader.add_value("url", f"{response.url}#route-{route['routeNumber']}")
            loader.add_value("source", self.name)
            loader.add_value("name", route.get("title"))
            loader.add_value("start", route.get("start"))
            loader.add_value("via", route.get("via"))
            loader.add_value("end", route.get("end"))
            loader.add_value("difficulty", route.get("grade"))
            loader.add_value("fitness", route.get("fitness"))
            loader.add_value("length_km", route.get("length"))
            loader.add_value("elevation_gain_m", route.get("ascent"))
            loader.add_value("stages", route.get("stages"))
            yield loader.load_item()