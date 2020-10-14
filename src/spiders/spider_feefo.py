import os
import re
import json
from scrapy import Spider
from scrapy import signals
from datetime import datetime
from scrapy import FormRequest
from src.items.item_feefo import  FeefoReviewItem

class FeefoSpider(Spider):
    name = "feefo"
    useragent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'
    base_url = 'https://www.feefo.com/en-GB/reviews/{trademark}?withMedia=false&timeFrame={timeframe}&displayFeedbackType=PRODUCT'
    start_urls = []
    connection = None

    sessions = {}

    headers = {
        'User-Agent': f'{useragent}',
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
        self.session_dir = kwargs.get('session_dir', '')

    @staticmethod
    def get_trademark(url):
        parts = url.split('?')[0].split('/')
        return parts[-1]

    @staticmethod
    def get_timeframe(url):
        result = re.search(r'(?<=timeFrame=).*?(?=[&$])', url)
        return result.group(0) if result else ''

    def _get_session(self, td_mark, time_frame):
        session_file_name = f'{td_mark}_{time_frame}.session'
        session_file_full_path = os.path.join(self.session_dir, session_file_name)
        lastDate = None
        lastId = None
        pageNumber = None
        reviews_counter = 0
        try:
            if os.path.exists(session_file_full_path):
                with open(session_file_full_path, 'r') as f_session:
                    session_dict = json.load(f_session)
                    lastDate = session_dict.get('lastDate', None)
                    lastId = session_dict.get('lastId', None)
                    pageNumber = session_dict.get('pageNumber', None)
                    reviews_counter = session_dict.get('reviews_counter', None)
        except Exception as exc:
            self.logger.error(f'SESSION ERROR. Exception: {exc}')
        return lastDate, lastId, pageNumber, reviews_counter

    def _save_session(self, td_mark, time_frame, lastDate, lastId,  pageNumber, reviews_counter):
        if td_mark and time_frame and lastDate and lastId and pageNumber:
            session_file_name = f'{td_mark}_{time_frame}.session'
            session_file_full_path = os.path.join(self.session_dir, session_file_name)
            session_dict = {'lastDate':lastDate, 'lastId':lastId,  'pageNumber':pageNumber, 'reviews_counter':reviews_counter}
            try:
                with open(session_file_full_path, 'w') as f_session:
                    json.dump(session_dict, f_session)
            except Exception as exc:
                self.logger.error(f'SESSION ERROR. Exception: {exc}')
                return False
            finally:
                return True
        return False

    def _delete_session(self, td_mark, time_frame):
        session_file_name = f'{td_mark}_{time_frame}.session'
        session_file_full_path = os.path.join(self.session_dir, session_file_name)
        if os.path.exists(session_file_full_path):
            os.remove(session_file_full_path)

    @classmethod
    def from_crawler(cls, crawler, *args, **kwargs):
        spider = super(FeefoSpider, cls).from_crawler(crawler, *args, **kwargs)
        crawler.signals.connect(spider.spider_error, signal=signals.spider_error)
        crawler.signals.connect(spider.spider_opened, signal=signals.spider_opened)
        #crawler.signals.connect(spider.spider_closed, signal=signals.spider_closed)
        return spider

    def parse(self, response):
        td_mark = self.get_trademark(response.url)
        time_frame = self.get_timeframe(response.url)
        headers = FeefoSpider.headers.copy()
        params = FeefoSpider.params.copy()
        headers['Referer'] = headers['Referer'].format(td_mark=td_mark, time_frame=time_frame)
        params['timeFrame'] = params['timeFrame'].format(time_frame=time_frame)
        pageNumber = response.meta.get('pageNumber', None)
        reviews_counter = response.meta.get('reviews_counter', 0)
        session_key = f'{td_mark}:{time_frame}'
        lastDate = None
        lastId = None
        session_restored = False
        # if pageNumber == '2':
        #     raise Exception('Boom!')
        if session_key in self.sessions:
            # Restore session
            lastDate = self.sessions[session_key]['lastDate']
            lastId = self.sessions[session_key]['lastId']
            pageNumber = self.sessions[session_key]['pageNumber']
            reviews_counter = self.sessions[session_key]['reviews_counter']
            params.update({'lastDate': lastDate, 'lastId': lastId, 'pageNumber': pageNumber})
            del self.sessions[session_key]
            req_pagination = FormRequest(f'https://www.feefo.com/api/feedbacks/lazy/{td_mark}',
                                         method='GET',
                                         formdata=params,
                                         headers=headers,
                                         meta={'pageNumber': pageNumber, 'reviews_counter': reviews_counter,
                                               'lastDate': lastDate, 'lastId': lastId},
                                         callback=self.parse)
            session_restored = True
            yield req_pagination

        if pageNumber is None:
            pageNumber = '0'
            params.update({'pageNumber': pageNumber})
            req_pagination = FormRequest(f'https://www.feefo.com/api/feedbacks/lazy/{td_mark}',
                                         method='GET',
                                         formdata=params,
                                         headers=headers,
                                         meta={'pageNumber': pageNumber, 'reviews_counter': reviews_counter,
                                               'lastDate': lastDate, 'lastId': lastId},
                                         callback=self.parse)
            yield req_pagination
        else:
            if not session_restored:
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
                                                 meta={'pageNumber': pageNumber, 'reviews_counter': reviews_counter,
                                                       'lastDate': lastDate, 'lastId': lastId},
                                                 callback=self.parse)
                    yield req_pagination
            else:
                self._delete_session(td_mark, time_frame)

    def spider_error(self, failure, response, spider):
        spider.logger.error(f'Spider {spider.name} exception {failure.value}')
        try:
            td_mark = self.get_trademark(response.url)
            time_frame = self.get_timeframe(response.url)
            lastDate = response.meta.get('lastDate', None)
            lastId =  response.meta.get('lastId', None)
            reviews_counter = response.meta.get('reviews_counter', 0)
            pageNumber = response.meta.get('pageNumber', None)
            self._save_session(td_mark, time_frame, lastDate, lastId, pageNumber, reviews_counter)
            self.logger.info(f'Saved session {td_mark} {time_frame} with parameters: lastDate={lastDate}, '
                             f'lastId={lastId}, pageNumber={pageNumber}, reviews_counter={reviews_counter}')
        except Exception as exc:pass

    def spider_opened(self, spider):
        for url in self.start_urls:
            td_mark = self.get_trademark(url)
            time_frame = self.get_timeframe(url)
            data = self._get_session(td_mark, time_frame)
            if all(data):
                lastDate, lastId, pageNumber, reviews_counter = data
                self.sessions[f'{td_mark}:{time_frame}'] = {'lastDate':lastDate, 'lastId':lastId, 'pageNumber':pageNumber,
                                                            'reviews_counter':reviews_counter}
                self.logger.info(f'Restored session {td_mark} {time_frame} with parameters: lastDate={lastDate}, '
                                 f'lastId={lastId}, pageNumber={pageNumber}, reviews_counter={reviews_counter}')
