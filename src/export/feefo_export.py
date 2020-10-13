import os
import pymysql
import pandas
from datetime import datetime
from src.utils.utils import mkdir_p
from dotenv import load_dotenv, find_dotenv

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

if __name__ == '__main__':
    load_dotenv(find_dotenv())
    dbhost = os.getenv("DBHOST")
    dbuser = os.getenv("DBUSER")
    dbpassword = os.getenv("DBPASSWORD")
    dbport = os.getenv("DBPORT")
    dbbase = os.getenv("DBBASE")
    csv_dir = os.path.abspath(os.getenv("CSVDIR", os.path.join(SCRIPT_DIR, 'Csv')))
    mkdir_p(csv_dir)

    if dbhost and dbport and dbbase and dbuser and dbpassword:
        try:
            conn = pymysql.connect(host=dbhost, port=int(dbport), database=dbbase, user=dbuser, password=dbpassword)
            query = 'select * from reviews'
            reviews = pandas.read_sql_query(query, conn)
            dt = datetime.now().strftime('%Y%m%d%H%M%S')
            mkdir_p(csv_dir)
            csv_file_name = os.path.join(csv_dir, f'{dt}.csv')
            reviews.to_csv(csv_file_name, index=False)
        except Exception as exc:
            print(f'Exception: {exc}')
        else:
            print(f'Succesfully created CSV file: {csv_file_name}')


