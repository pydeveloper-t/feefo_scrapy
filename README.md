# feefo_scrapy

The Scrapy based parser for crawling feefo.com



## Requirements

- Python 3.6
- MySQL 
- pipenv(pip)


## How to install?
- Install python 3.6 (https://www.python.org/downloads/release/python-360/)
- Install pipenv
```
	pip install  pipenv
```	
- Clone repo to local disk
```
	git clone https://github.com/pydeveloper-t/feefo_scrapy . 
```	
- Set an environment variable to place virtual environment in the same folder
```
	set export PIPENV_VENV_IN_PROJECT=1
```	
-  Installing all neccessary packages
```
    cd <project_folder>
    pipenv install --ignore-pipfile
```	





### Edit configuration file (.env)
Set 
- the actual credentials for MySQL:  DBHOST, DBPORT, DBBASE, DBUSER, DBPASSWORD 
- path (absolute or relative) for storing log-files: LOGDIR
- path for output csv files: CSVDIR
- path to file with trademarks slugs list for scraping: TRADEMARKS
- TIMEFRAME – time-frame for crawling data from site (WEEK,  MONTH,  SIX_MONTHS, YEAR, ALL)
 

```
TRADEMARKS = ./feefo_scrapy/src/urls/feefo_urls
TIMEFRAME  = ALL
LOGDIR     = './Log'
CSVDIR     = './Csv'
DBHOST     = localhost
DBPORT     = 3306
DBBASE     = tesco
DBUSER     = xxxxxxxxxxx
DBPASSWORD = xxxxxxxxxxx

```

Example of Trademarks slugs file (for url https://www.feefo.com/en-GB/reviews/tm-lewin?withMedia=false&timeFrame=YEAR&displayFeedbackType=PRODUCT)

```
tm-lewin
```

### Run spider
```
pipenv run  python ./start/run_feefo.py
```

  
### Additional Information
> Alembic a database migration toop used in this project for  perform migrations to handle changes to the database. (See https://alembic.sqlalchemy.org/en/latest/index.html)

```
alembic current
alembic revision --autogenerate -m "Description of migration"
alembic upgrade head
```

