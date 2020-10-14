import logging
import os, sys
from dotenv import load_dotenv, find_dotenv
sys.path.insert(0, os.path.abspath(__file__ + "/../../../"))
from datetime import datetime
from scrapy.crawler import CrawlerProcess
from src.utils.utils import mkdir_p
from scrapy.utils.log import configure_logging
from src.database.Connection import Connection
from scrapy.utils.project import get_project_settings
from src.spiders.spider_feefo import FeefoSpider

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    trademarks_list_file = os.getenv("TRADEMARKS")
    timeframe = os.getenv("TIMEFRAME")
    configure_logging(install_root_handler=False)
    session_dir = os.path.abspath(os.getenv("SESSIONDIR"))
    mkdir_p(session_dir)
    log_dir = os.path.abspath(os.getenv("LOGDIR", os.path.join(SCRIPT_DIR, 'Log')))
    log_file_name = 'feefo_' + str(datetime.utcnow())[:19].replace('-', '').replace(':', '').replace(' ', '_') + '.log'
    mkdir_p(log_dir)
    logging.basicConfig(
        filename=os.path.join(log_dir, log_file_name),
        format='%(levelname)s: %(message)s',
        level=logging.INFO
    )
    if trademarks_list_file and timeframe:
        try:
            with open(os.path.abspath(trademarks_list_file), 'r') as f:
                trademarks = f.readlines()
        except Exception as exc:
            print(f'File {trademarks_list_file} open error: {exc}')
            raise SystemExit
        else:
            start_urls = [ FeefoSpider.base_url.format(trademark=trademark.strip(), timeframe=timeframe)  for trademark in  trademarks]
            process = CrawlerProcess(get_project_settings())
            process.crawl(FeefoSpider, start_urls=start_urls, session_dir=session_dir, connection=Connection() )
            process.start()
            process.stop()

