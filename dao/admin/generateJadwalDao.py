from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_URLS_COLLECTION as db_urls
from flask import session

class generateJadwalDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)