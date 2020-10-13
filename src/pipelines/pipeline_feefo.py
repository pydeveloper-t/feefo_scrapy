import os, csv
from datetime import datetime
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
        dt = datetime.now().strftime('%Y%m%d%H%M%S')
        csv_file_name = os.path.join(spider.csv_dir, f'{dt}.csv')
        with open(csv_file_name, 'w', encoding='utf8', newline='')  as f:
            dict_writer = csv.DictWriter(f, self.records[0].keys(), delimiter=',', quotechar='"', quoting=csv.QUOTE_ALL)
            dict_writer.writeheader()
            dict_writer.writerows(self.records)
            print(f'Created CSV-file {csv_file_name} with {len(self.records)} records')
        for record in self.records:
            insert_stmt = insert(FeefoReview).values(record)
            on_duplicate_stmt = insert_stmt.on_duplicate_key_update(record)
            spider.connection.session.execute(on_duplicate_stmt)
        spider.connection.session.commit()
        spider.connection.session.close()
