import os, csv
from datetime import datetime
from src.database.models.feefo_review import reviews
from sqlalchemy.dialects.mysql import insert

class FeefoScraperPipeline:
    def process_item(self, item, spider):
        return self.handleReview(item, spider)

    def handleReview(self, item, spider):
        record = dict(item)
        insert_stmt = insert(reviews).values(record)
        on_duplicate_stmt = insert_stmt.on_duplicate_key_update(record)
        spider.connection.engine.execute(on_duplicate_stmt)
