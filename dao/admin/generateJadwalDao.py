from dao import Database
from config import MONGO_DB, MONGO_LECTURERS_COLLECTION as db_dosen, MONGO_OPEN_COURSES_COLLECTION as db_matkul, MONGO_CLASSES_COLLECTION as db_kelas
from flask import session

class generateJadwalDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_dosen(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Dosen")
        result = self.connection.find_many(db_dosen)
        return result['data'] if result and result.get('status') else []
    
    def get_matkul(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul")
        result = self.connection.find_many(db_matkul)
        return result['data'] if result and result.get('status') else []
    
    def get_kelas(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get kelas")
        result = self.connection.find_many(db_kelas)
        return result['data'] if result and result.get('status') else []