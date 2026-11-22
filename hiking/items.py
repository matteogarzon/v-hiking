# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from itemloaders.processors import Join, MapCompose, TakeFirst
import scrapy
import re

def clean_text(value):
    """Remove extra whitespace and newlines."""
    return " ".join(value.split())

def to_int(value):
    """Convert a string to an integer, extracting digits if necessary."""
    if isinstance(value, (int, float)):
        return int(value)
    m = re.search(r"\d+", value.replace("'", "").replace(".", ""))
    return int(m.group()) if m else None

class TrailItem(scrapy.Item):
    """Represents a trail item."""
    # define the fields for your item here like:
    # name: str | None = None

    url = scrapy.Field(output_processor=TakeFirst())
    source = scrapy.Field(output_processor=TakeFirst())       # which website it came from
    name = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    
    start = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    via = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join(" | "))  # all intermediate places
    end = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    difficulty = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    fitness = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=TakeFirst())
    
    length_km = scrapy.Field(output_processor=TakeFirst())
    stages = scrapy.Field(output_processor=TakeFirst())
    elevation_gain_m = scrapy.Field(output_processor=TakeFirst())
    duration = scrapy.Field(output_processor=TakeFirst())     # e.g. "4h30" (komoot)
    rating = scrapy.Field(output_processor=TakeFirst())       # average user rating (komoot)
    description = scrapy.Field(input_processor=MapCompose(clean_text), output_processor=Join(" "))