import re
import json
from scrapy import Spider
from datetime import datetime
from scrapy import FormRequest
from src.items.item_feefo import  FeefoReviewItem

class FeefoSpider(Spider):
    name = "feefo"
    useragent = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:80.0) Gecko/20100101 Firefox/80.0'
    base_url = 'https://www.feefo.com/en-GB/reviews/{trademark}?withMedia=false&timeFrame={timeframe}&displayFeedbackType=PRODUCT'
    start_urls = []
    connection = None

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'en-US,en;q=0.5',
        'Connection': 'keep-alive',
        'Referer': 'https://www.feefo.com/en-GB/reviews/{td_mark}?withMedia=false&timeFrame={time_frame}&displayFeedbackType=PRODUCT',
        'Cache-Control': 'max-age=0',
        'TE': 'Trailers',
    }

    params = {
        'displayFeedbackType':'PRODUCT',
        'locale':'en-gb',
        'pageNumber': None,
        'sort': 'newest',
        'tags':'{}',
        'timeFrame': '{time_frame}',
        'withMedia':'false'
    }

    def __init__(self, **kwargs):
        self.start_urls = kwargs.get('start_urls', [])
        self.connection = kwargs.get('connection', None)

    @staticmethod
    def get_trademark(url):
        parts = url.split('?')[0].split('/')
        return parts[-1]

    @staticmethod
    def get_timeframe(url):
        result = re.search(r'(?<=timeFrame=).*?(?=[&$])', url)
        return result.group(0) if result else ''

    def parse(self, response):
        td_mark = FeefoSpider.get_trademark(response.url)
        time_frame = FeefoSpider.get_timeframe(response.url)
        headers = FeefoSpider.headers.copy()
        params = FeefoSpider.params.copy()
        headers['Referer'] = headers['Referer'].format(td_mark=td_mark, time_frame=time_frame)
        params['timeFrame'] = params['timeFrame'].format(time_frame=time_frame)
        pageNumber = response.meta.get('pageNumber', None)
        reviews_counter = response.meta.get('reviews_counter', 0)
        if pageNumber is None:
            pageNumber = '0'
            params['pageNumber'] = pageNumber
            req_pagination = FormRequest(f'https://www.feefo.com/api/feedbacks/lazy/{td_mark}',
                                         method='GET',
                                         formdata=params,
                                         headers=headers,
                                         meta={'pageNumber':pageNumber, 'reviews_counter':0},
                                         callback=self.parse)
            yield req_pagination
        else:
            json_data = json.loads(response.text)
            for sale in json_data.get('sales', []):
                for item in sale.get('saleItems', []):
                    review_item = FeefoReviewItem()
                    product_feedback = item.get('productFeedback', {})
                    review_item['external_id'] = product_feedback.get('id', None)
                    review_item['product_name'] = item.get('name', None)
                    review_item['review'] = product_feedback.get('consumerComment', None)
                    review_item['rating'] = product_feedback.get('numericalScore', None)
                    review_item['location'] = sale.get('region', None)
                    review_item['author'] = sale.get('consumerDisplayName', 'Trusted Customer')
                    review_item['purchase_date'] = datetime.utcfromtimestamp(int(sale.get('saleDate', '')/1000)).strftime('%Y-%m-%d %H:%M:%S')
                    reviews_counter+=1
                    self.logger.info(f"Page {pageNumber} Processed reviews: {reviews_counter}")
                    yield review_item
            pageNumber= str(int(pageNumber) + 1)
            if json_data.get('hasMore', False):
                lastDate = str(json_data.get('lastDate'))
                lastId = json_data.get('lastId')
                params.update({'lastDate': lastDate, 'lastId': lastId, 'pageNumber': pageNumber})
                req_pagination = FormRequest(f'https://www.feefo.com/api/feedbacks/lazy/{td_mark}',
                                             method='GET',
                                             formdata=params,
                                             headers=headers,
                                             meta={'pageNumber': pageNumber, 'reviews_counter': reviews_counter},
                                             callback=self.parse)
                yield req_pagination

