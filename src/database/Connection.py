import os
from src.database import metadata
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class Connection:
    def __init__(self):
        self.engine = self.db_connect()
        self.create_tables(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    @staticmethod
    def _get_connection_string():
        dbhost = os.getenv("DBHOST")
        dbuser = os.getenv("DBUSER")
        dbpassword = os.getenv("DBPASSWORD")
        dbport = os.getenv("DBPORT")
        dbbase = os.getenv("DBBASE")
        return  f'mysql+pymysql://{dbuser}:{dbpassword}@{dbhost}:{dbport}/{dbbase}'

    def create_tables(self, engine):
        metadata.create_all(engine)

    def db_connect(self):
        return create_engine(Connection._get_connection_string())

