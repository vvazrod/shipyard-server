import os

from pymongo import MongoClient


db_name = os.getenv('DB_NAME')
if db_name is None:
    exit(-1)

client = MongoClient(host='db')[db_name]
