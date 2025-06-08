import pymysql, os
from config import settings

def get_conn():
    return pymysql.connect(
        host=settings.DB_HOST,
        user=settings.DB_USER,
        password=settings.DB_PASS,
        database=settings.DB_NAME,
        port=settings.DB_PORT,
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=True
    )

