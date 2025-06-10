from dao import Database
from config import MONGO_DB, MONGO_CLASSES_COLLECTION as db_kelas
from flask import session

from global_func import CustomError

PRAKTIKUM_RELATED = ['os', 'processor', 'ram', 'storage']

class dataRuanganDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)


    def post_kelas(self, params):
        print(f"{'':<7}{'[ DAO ]':<8} Post Kelas (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Ruangan belum diisi!' })
            elif not params.get('tipe_ruangan'):
                raise CustomError({ 'message': 'Tipe Ruangan belum diisi!' })
            elif not params.get('kapasitas'):
                raise CustomError({ 'message': 'Kapasitas Ruangan belum diisi!' })
            
            isExist = self.connection.find_one(db_kelas, {'kode': params['kode']})
            if isExist['status'] == True:
                raise CustomError({ 'message': f"Data dengan Kode Ruangan {params['kode']} sudah ada!" })

            if params['tipe_ruangan'] != "PRAKTIKUM":
                for x in PRAKTIKUM_RELATED:
                    params.pop(x, None)
            params = {k: v for k, v in params.items() if v}

            res = self.connection.insert_one(db_kelas, params)
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def put_kelas(self, params):
        print(f"{'':<7}{'[ DAO ]':<8} Put Kelas (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Ruangan belum diisi!' })
            elif not params.get('tipe_ruangan'):
                raise CustomError({ 'message': 'Tipe Ruangan belum diisi!' })
            elif not params.get('kapasitas'):
                raise CustomError({ 'message': 'Kapasitas Ruangan belum diisi!' })
            
            isExist = self.connection.find_one(db_kelas, {'kode': params['kode']})
            if isExist['status'] == True:
                raise CustomError({ 'message': f"Data dengan Kode Ruangan {params['kode']} sudah ada!" })

            unset = {k: "" for k, v in params.items() if not v}
            if params['tipe_ruangan'] != "PRAKTIKUM":
                for x in PRAKTIKUM_RELATED:
                    params.pop(x, None)
                    if x not in unset: unset[x] = ""
            params = {k: v for k, v in params.items() if v}

            res = self.connection.update_one(db_kelas, {'kode': params['kode']}, params, unset)
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def delete_kelas(self, list_kode):
        print(f"{'':<7}{'[ DAO ]':<8} Delete Kelas (List Kode: {list_kode})")
        result = { 'status': False }

        try:
            res = self.connection.delete_many(
                db_kelas, 
                {'kode': { '$in': list_kode }}
            )
            if res['status'] == True:
                result.update({ 'status': True, 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result