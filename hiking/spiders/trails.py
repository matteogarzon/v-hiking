import scrapy

# Spider: class that says where to start and how to parse each response
class TrailsSpider(scrapy.Spider):
    name = "trails"
    allowed_domains = ["www.myswitzerland.com"] # stops the crawl from leaving the website 
    start_urls = [
        "https://www.myswitzerland.com/it-ch/scoprire-la-svizzera/estate-autunno/escursionismo/a-piedi-ricerca/?_gl=1*1r48iyh*_up*MQ..*_ga*ODQzNDk1My4xNzk1MjUyNTI2*_ga_F6N1LVHY7B*czE3OTUyNTI1MjYkbzEkZzAkdDE3OTUyNTI1OTIkajYwJGwwJGgxNjY3MDAyNTcx*guuruGa_ga*MTczMDI4OTEyMC4xNzk1MjUyNTI2*guuruGa_ga_R8RBFL040X*czE3OTUyNTI1MjYkbzEkZzAkdDE3OTUyNTI1OTIkajYwJGwwJGgw"
        ]

    def parse(self, response):
        """Follow every trail link, then the next page."""

        for href in response.css("a.OfferTeaser--link::attr(href)").getall():
            yield response.follow(href, callback=self.parse_trail) # yield returns the result and continues to the next step

        next_page = response.css("a.Pagination--link.next::attr(href)").get()
        if next_page:
            yield response.follow(next_page, callback=self.parse) #queues another page to crawl

    def parse_trail(self, response):
        """Detail page: extract one record."""
        yield {
            "url": response.url,
            "name": response.css("h1::text").get(default="").strip(),
            "start": response.css(".start::text").get(default="").strip(),
            "end": response.css(".end::text").get(default="").strip(),
            "difficulty": response.css(".difficulty::text").get(),
            "length_km": response.css(".length::text").re_first(r"([\d.,]+)\s*km"),
            "elevation_gain_m": response.css(".elevation::text").re_first(r"(\d+)"),
            "description": " ".join(response.css(".description ::text").getall()).strip(),
        }