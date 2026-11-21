import json
import re

from scrapy.linkextractors import LinkExtractor
from scrapy.loader import ItemLoader
from scrapy.spiders import CrawlSpider, Rule

from hiking.items import TrailItem


class KomootSpider(CrawlSpider):
    """Komoot tour pages are server-rendered and embed schema.org JSON-LD
    (a "Trip" object) with name, description, distance, duration, difficulty,
    rating and an itinerary of places. Komoot's /api and /webapi are disallowed
    in robots.txt, so we only read the public HTML pages."""

    name = "komoot"
    allowed_domains = ["www.komoot.com"]
    start_urls = ["https://www.komoot.com/guide/525/hiking-in-switzerland"]

    rules = (
        # Tour pages -> parse. follow=True so "similar tours" on each tour page are discovered too.
        # need to test with follow=False: smarttours with True may leave Switzterland
        Rule(LinkExtractor(allow=r"/smarttour/[\w-]+/[\w-]+$"), callback="parse_trail", follow=True),
        # Other hiking guides (regions, "easy hikes", "waterfall hikes", ...) -> just follow.
        Rule(LinkExtractor(allow=r"/guide/\d+/[\w-]*hik[\w-]*$"), follow=True),
    )

    custom_settings = {
        "DOWNLOAD_DELAY": 2,          # komoot pages are big (~3 MB); be gentle
    }

    def parse_trail(self, response):
        trip = self.get_trip_jsonld(response)
        if trip is None:
            return

        props = {p.get("name"): p.get("value") for p in trip.get("additionalProperty", [])}
        if props.get("Sport") not in (None, "Hiking"):
            return  # skip running/biking tours that guides may link to

        places = [
            el["item"]["name"]
            for el in trip.get("itinerary", {}).get("itemListElement", [])
            if el.get("item", {}).get("name")
        ]

        loader = ItemLoader(item=TrailItem(), response=response)
        loader.add_value("url", response.url)
        loader.add_value("source", self.name)
        loader.add_value("name", trip.get("name"))
        loader.add_value("description", trip.get("description"))
        loader.add_value("difficulty", props.get("Difficulty"))            # "Easy" / "Moderate" / "Difficult"
        loader.add_value("length_km", self.km(props.get("Distance")))     # "12.2 km" -> 12.2
        loader.add_value("duration", self.iso_duration(props.get("Duration")))  # "PT4H30M" -> "4h30"
        if places:
            loader.add_value("start", places[0])
            loader.add_value("end", places[-1])
            loader.add_value("via", places[1:-1])    # list of highlights in between
        rating = trip.get("aggregateRating", {}).get("ratingValue")
        loader.add_value("rating", float(rating) if rating else None)
        # Elevation is not in the JSON-LD, but the page shows it in a stable test-id element.
        loader.add_value("elevation_gain_m", self.to_int(
            "".join(response.css('[data-test-id="t_elevation_up"] span::text').getall())
        ))
        yield loader.load_item()

    # ---------- helpers ----------

    @staticmethod
    def get_trip_jsonld(response):
        for raw in response.xpath('//script[@type="application/ld+json"]/text()').getall():
            try:
                data = json.loads(raw)
            except json.JSONDecodeError:
                continue
            types = data.get("@type", [])
            if "Trip" in (types if isinstance(types, list) else [types]):
                return data
        return None

    @staticmethod
    def km(text):
        m = re.search(r"[\d.]+", text or "")
        return float(m.group()) if m else None

    @staticmethod
    def to_int(text):
        m = re.search(r"\d+", (text or "").replace(",", "").replace("'", ""))
        return int(m.group()) if m else None

    @staticmethod
    def iso_duration(text):
        m = re.fullmatch(r"PT(?:(\d+)H)?(?:(\d+)M)?", text or "")
        if not m:
            return None
        h, mnt = int(m.group(1) or 0), int(m.group(2) or 0)
        return f"{h}h{mnt:02d}"
