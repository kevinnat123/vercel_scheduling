from dao import Database
from config import MONGO_DB, MONGO_MAJOR_COLLECTION as db_prodi
from flask import session, current_app
from datetime import datetime, timezone

from global_func import CustomError

class dataProgramStudiDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_prodi(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Program Studi")
        if session['user']['role'] == "ADMIN":
            result = self.connection.find_many(
                db_prodi, 
                sort=[("status_aktif", -1), ("program_studi", 1)]
            )
            if result and result.get('data'):
                for data in result['data']:
                    data.setdefault('kepala_program_studi', None)
        return result['data'] if result and result.get('status') else []
    
    def post_prodi(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Post Prodi (Parameter: {params})")
        result = { 'status': False }

        try:
            if session['user']['role'] != "ADMIN":
                raise CustomError({ 'message': 'Anda tidak berhak!' })

            if not params.get('program_studi'):
                raise CustomError({ 'message': 'Nama Program Studi belum diisi!', 'target': 'input_prodi' })
            elif not params.get('status'):
                raise CustomError({ 'message': 'Status Program Studi belum diisi!' })
            
            # Check exist
            res = self.connection.find_one(db_prodi, {'program_studi': params['program_studi']})
            if (res['status'] == True):
                raise CustomError({ 'message': 'Data Program Studi sudah ada!' })
                
            # Hapus key yang memiliki value kosong
            params["status_aktif"] = True if params.pop("status_aktif", None) == "AKTIF" else False
            params = {k: v for k, v in params.items() if v}
                
            res = self.connection.insert_one(db_prodi, params)

            if res['status'] == True:
                current_app.last_updated = datetime.now(timezone.utc)
                result.update({ 'message': res['message'] })
            else:
                raise CustomError({ 'message': res['message'] })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result