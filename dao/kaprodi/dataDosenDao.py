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
            if not params.get('nip'):
                raise CustomError({ 'message': 'NIP belum diisi!', 'target': 'input_nip' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            elif not params.get("status"):
                raise CustomError({ 'message': 'Status Dosen belum diisi!' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            
            # Check exist
            res = self.connection.find_one(db_dosen, {'nip': params['nip']})
            if (res['status'] == True):
                raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' sudah ada!' })
            if session['user']['role'] == "KAPRODI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
                
            # Hapus key yang memiliki value kosong
            if params.get('preferensi'):
                if params['preferensi'].get('value'):
                    params['preferensi'] = {k: v for k, v in params['preferensi'].items() if v}
                    params['preferensi'].pop('value')
                else:
                    params.pop('preferensi')
            params = {k: v for k, v in params.items() if v}
                
            res = self.connection.insert_one(db_dosen, params)

            # update matkul
            if params.get('matkul_ajar'):
                for matkul in params['matkul_ajar']:
                    exist = self.connection.find_one(db_matkul, {"nama": matkul})
                    if exist and exist.get('status'):
                        dosen_ajar_lama = exist['data'].get('dosen_ajar') or []
                        if params['nama'] not in dosen_ajar_lama:
                            dosen_ajar_lama.append(params['nama'])
                            self.connection.update_one(db_matkul, {"nama": matkul}, {"dosen_ajar": dosen_ajar_lama})

            if res['status'] == True:
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
    
    def put_dosen(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Put Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('nip'):
                raise CustomError({ 'message': 'NIP belum diisi!' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama belum diisi!', 'target': 'input_nama' })
            elif not params.get('status'):
                raise CustomError({ 'message': 'Status Dosen belum diisi!' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            
            # Check exist
            dosen_exist = self.connection.find_one(db_dosen, {'nip': params['nip']})
            if (dosen_exist['status'] == False and dosen_exist['data'] == None):
                raise CustomError({ 'message': 'Data dengan NIP ' + params['nip'] + ' tidak ditemukan!' })

            if session['user']['role'] == "KAPRODI":    
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda mengubah program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
            
            unset = {k: "" for k, v in params.items() if not v}

            if params.get('preferensi'):
                if params['preferensi'].get('value'):
                    params['preferensi'].pop('value')

                    # params['preferensi'] = {k: v for k, v in params['preferensi'].items() if v}
                    for k, v in dict(params['preferensi']).items():
                        if v:
                            continue
                        else:
                            unset[f'preferensi.{k}'] = ""
                            params['preferensi'].pop(k)

                    if not params['preferensi']:
                        params.pop('preferensi')
                        unset = {k: v for k, v in unset.items() if not k.startswith('preferensi.')}
                        unset['preferensi'] = ""
                else:
                    params.pop('preferensi')
                    unset['preferensi'] = ""

            params = {k: v for k, v in params.items() if v}
                
            res = self.connection.update_one(db_dosen, {'nip': params['nip']}, params, unset)

            # update matkul
            if params.get('matkul_ajar'):
                for matkul in params['matkul_ajar']:
                    exist = self.connection.find_one(db_matkul, {"nama": matkul})
                    if exist and exist.get('status'):
                        dosen_ajar_lama = exist['data'].get('dosen_ajar') or []
                        if params['nama'] not in dosen_ajar_lama:
                            dosen_ajar_lama.append(params['nama'])
                            self.connection.update_one(db_matkul, {"nama": matkul}, {"dosen_ajar": dosen_ajar_lama})

            if len(params.get('matkul_ajar') or []) < len(dosen_exist['data'].get('matkul_ajar') or []):
                matkul_ajar_lama = dosen_exist['data'].get('matkul_ajar') or []
                matkul_ajar_baru = params.get('matkul_ajar') or []
                data_dihapus = [dt for dt in matkul_ajar_lama if dt not in matkul_ajar_baru]

                for matkul in data_dihapus:
                    data_matkul = self.connection.find_one(db_matkul, {'nama': matkul})
                    if data_matkul and data_matkul.get('status'):
                        old_data = data_matkul['data']
                        old_data['dosen_ajar'].remove(params['nama'])
                        if old_data['dosen_ajar']:
                            self.connection.update_one(db_matkul, {'nama': matkul}, {'dosen_ajar': old_data['dosen_ajar']})
                        else:
                            self.connection.update_one(db_matkul, {'nama': matkul}, {}, {'dosen_ajar': ""})
                    else:
                        raise Exception
            
            if res['status'] == True:
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
    
    def delete_dosen(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Delete Dosen (Parameter: {params})")
        result = { 'status': False }

        try:
            list_nip = [item["nip"] for item in params]
            for nip in list_nip:
                data_dosen = self.connection.find_one(db_dosen, {'nip': nip})
                if data_dosen and data_dosen.get('status'):
                    data_dosen = data_dosen['data']
                    matkul_ajar_dosen = data_dosen.get('matkul_ajar') or []
                    for matkul in matkul_ajar_dosen:
                        data_matkul = self.connection.find_one(db_matkul, {'nama': matkul})
                        if data_matkul and data_matkul.get('status'):
                            data_matkul = data_matkul['data']
                            data_matkul['dosen_ajar'].remove(data_dosen['nama'])
                            if data_matkul['dosen_ajar']:
                                self.connection.update_one(db_matkul, {'nama': matkul}, {'dosen_ajar': data_matkul['dosen_ajar']})
                            else:
                                self.connection.update_one(db_matkul, {'nama': matkul}, {}, {'dosen_ajar': ""})
                        else:
                            raise Exception
                else:
                    raise Exception
                
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

        return result
    
    def get_matkul(self, prodi: str):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul (Prodi: {prodi})")
        result = self.connection.find_many(db_matkul, {'prodi': prodi}, sort=[("kode", 1)])
        return result['data'] if result and result.get('status') else None