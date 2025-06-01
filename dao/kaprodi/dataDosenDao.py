from dao import Database
from config import MONGO_DB, MONGO_LECTURERS_COLLECTION as db_dosen, MONGO_COURSES_COLLECTION as db_matkul
from flask import session

class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

class dataDosenDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_dosen(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Dosen (Prodi: {session['user']['prodi']})")
        result = self.connection.find_many(db_dosen, {'prodi': session['user']['prodi']}, sort=[("nip", 1)])
        if result.get('status'):
            for y in result['data']:
                if not y.get('pakar'):
                    y.update({ 'pakar': '' })
        return result['data'] if result and result.get('status') else None
    
    def post_dosen(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Post Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            # Hapus key yang memiliki value kosong
            params = {k: v for k, v in params.items() if v}
            if params.get('preferensi'):
                params['preferensi'] = {k: v for k, v in params['preferensi'].items() if v}
            print(f"params {params}")

            if params.get('nip'):
                # Check exist
                res = self.connection.find_one(db_dosen, {'nip': params['nip']})
                if (res['status'] == True):
                    raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' sudah ada!' })

                if params.get('nama'):
                    if params.get("status"):
                        if session['user']['role'] == "KAPRODI":
                            params.update({'prodi': session['user']['prodi']})
                            
                        res = self.connection.insert_one(db_dosen, params)

                        if res['status'] == True:
                            result.update({ 'message': res['message'] })
                        else:
                            raise CustomError({ 'message': res['message'] })
                    else:
                        raise CustomError({ 'message': 'Status Dosen belum diisi!' })
                else:
                    raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            else:
                raise CustomError({ 'message': 'NIP belum diisi!', 'target': 'input_nip' })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        print(f"{'':<15} Result: {result}")
        return result
    
    def put_dosen(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Put Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            if params.get('nip'):
                # Check exist
                res = self.connection.find_one(db_dosen, {'nip': params['nip']})
                if (res['status'] == False and res['data'] == None):
                    raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' tidak ditemukan!' })

                if params.get('nama'):
                    params.update({'prodi': session['user']['prodi']})
                    res = self.connection.update_one(db_dosen, {'nip': params['nip']}, params)
                    if res['status'] == False:
                        raise CustomError({ 'message': res['message'] })
                    else:
                        result.update({ 'message': res['message'] })
                else:
                    raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            else:
                raise CustomError({ 'message': 'NIP belum diisi!' })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        print(f"{'':<15} Result: {result}")
        return result
    
    def delete_dosen(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Delete Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            list_nip = [item["nip"] for item in params]
            res = self.connection.delete_many(
                db_dosen, 
                { 
                    'nip' : { '$in': list_nip }, 
                    'prodi': session['user']['prodi'] 
                }
            )
            if res['status'] == False:
                raise CustomError({ 'message': res['message'] })
            else:
                result.update({ 'status': True, 'message': res['message'] })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        print(f"{'':<15} Result: {result}")
        return result
    
    def get_matkul(self, prodi: str):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul (Prodi: {prodi})")
        result = self.connection.find_many(db_matkul, {'prodi': prodi}, sort=[("kode", 1)])
        return result['data'] if result and result.get('status') else None