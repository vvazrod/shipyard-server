"""
Database connection.
"""

import os

import pymongo

dbhost = os.getenv('DB_HOST', default='localhost')
db = pymongo.MongoClient(dbhost).shipyard
