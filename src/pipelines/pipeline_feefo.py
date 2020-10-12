from src.items.item_feefo import FeefoReviewItem
from src.database.models.feefo_review import FeefoReview
from sqlalchemy.dialects.mysql import insert

class FeefoScraperPipeline:
    records = []
    def process_item(self, item, spider):
        if isinstance(item, FeefoReviewItem):
            return self.handleReview(item, spider)

    def handleReview(self, item, spider):
        #row = FeefoReview(**item)
        self.records.append(dict(item))
        #self.records.append(item)
        #self.records.update({row.external_id:row})
        #spider.connection.session.add(row)

    def close_spider(self, spider):
        for record in self.records:
            insert_stmt = insert(FeefoReview).values(record)
            on_duplicate_stmt = insert_stmt.on_duplicate_key_update(record)
            spider.connection.session.execute(on_duplicate_stmt)
        spider.connection.session.commit()
        spider.connection.session.close()
