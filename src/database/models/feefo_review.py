from src.database import Base
from sqlalchemy import Column, String, Text, TIMESTAMP, DATETIME
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy import func, text


class FeefoReview(Base):
    __tablename__ = 'reviews'
    id = Column(BIGINT(20), primary_key=True, autoincrement=True)
    external_id = Column(String(255, collation='utf8mb4_unicode_ci'), unique=True, nullable=False)
    author = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False, index=True)
    product_name = Column(String(255, collation='utf8mb4_unicode_ci'), nullable=False)
    review = Column(Text(collation='utf8mb4_unicode_ci'))
    rating = Column(TINYINT(3, unsigned=True), nullable=False, index=True)
    location = Column(String(768, collation='utf8mb4_unicode_ci'), nullable=True)
    purchase_date = Column(DATETIME, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=func.now())
    updated_at = Column(TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), index=True)
    #UniqueConstraint('external_id', name='external_id')

    def __init__(self, **kwargs):
        self.external_id = kwargs['external_id']
        self.author = kwargs['author']
        self.product_name = kwargs['product_name']
        self.review = kwargs['review']
        self.rating = kwargs['rating']
        self.location = kwargs['location']
        self.purchase_date = kwargs['purchase_date']

    def __repr__(self):
        return "<Data %s, %s>, %s, %s" % (self.external_id, self.product_name, self.purchase_date, self.review)
