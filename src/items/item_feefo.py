import scrapy

class FeefoReviewItem(scrapy.Item):
    external_id = scrapy.Field()
    author = scrapy.Field()
    product_name = scrapy.Field()
    review = scrapy.Field()
    rating = scrapy.Field()
    location = scrapy.Field()
    purchase_date = scrapy.Field()


