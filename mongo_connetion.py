from pymongo import MongoClient

client = MongoClient('mongodb://15.164.217.239', 27017, username="root", password="root")


def get_mongo_connection():
    db = client.prosncons
    return db
