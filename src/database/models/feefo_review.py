from src.database import metadata
from sqlalchemy import func, text
from sqlalchemy.dialects.mysql import TINYINT, BIGINT
from sqlalchemy import Table, Column, String, Text, TIMESTAMP, DATETIME


reviews = Table('reviews', metadata,
                Column('id', BIGINT(20), primary_key=True, autoincrement=True),
                Column('external_id', String(255, collation='utf8mb4_unicode_ci'), unique=True, nullable=False),
                Column('author', String(255, collation='utf8mb4_unicode_ci'), nullable=False, index=True),
                Column('product_name', String(255, collation='utf8mb4_unicode_ci'), nullable=False),
                Column('review',Text(collation='utf8mb4_unicode_ci')),
                Column('rating', TINYINT(3, unsigned=True), nullable=False, index=True),
                Column('location', String(768, collation='utf8mb4_unicode_ci'), nullable=True),
                Column('purchase_date', DATETIME, nullable=True),
                Column('created_at', TIMESTAMP, nullable=False, server_default=func.now()),
                Column('updated_at', TIMESTAMP, nullable=False, server_default=text('CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP'), index=True)
          )




