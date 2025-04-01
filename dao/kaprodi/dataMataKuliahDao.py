from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_COURSES_COLLECTION as db_courses
from flask import session

class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

class dataMataKuliahDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def put_kelompok(self, nama_baru):
        result = { 'status': False }
        print('  [ DAO ] put kelompok')
        try:
            if nama_baru.upper() in session['user']['kelompok_matkul']:
                raise CustomError({ 'message': 'Kelompok dengan nama ' + nama_baru.upper() + ' sudah ada!' })

            session['user']['kelompok_matkul'].extend([nama_baru.upper()])
            result = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'kelompok_matkul': session['user']['kelompok_matkul']})
            if result and result.get('status') == False:
                session['user']['kelompok_matkul'].remove(nama_baru.upper())
                raise Exception

            result.update({ 'status': True, 'message': result.get('message') })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
        except Exception as e:
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        session.modified = True  # Pastikan perubahan tersimpan
        return result
    
    def get_matkul(self):
        print('  [ DAO ] get matkul', session['user']['prodi'])
        result = self.connection.find_many(db_courses, {'program_studi': { '$in' : ['GENERAL', session['user']['prodi']] }})
        return result['data'] if result and result.get('status') else None
    
    def post_matkul(self, params: dict):
        result = { 'status': False }
        print('  [ DAO ] post matkul', params)

        try:
            # Hapus key yang memiliki value kosong
            params = {k: v for k, v in params.items() if v}
            print('    params', params)

            if params.get('kode'):
                # Check exist
                res = self.connection.find_one(db_courses, {'kode': params['kode']})
                if (res['status'] == True):
                    raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' sudah ada!' })

                if params.get('nama'):
                    if params.get('sks_akademik') and params.get('sks_bayar'):
                        params.update({'prodi': session['user']['prodi']})
                        res = self.connection.insert_one(db_courses, params)
                        if res['status'] == False:
                            raise CustomError({ 'message': res['message'] })
                        else:
                            result.update({ 'message': res['message'] })
                    else:
                        raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
                else:
                    raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
            else:
                raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        print('    result', result)
        return result
    
    def put_matkul(self, params: dict):
        result = { 'status': False }
        print('  [ DAO ] put matkul')

        try:
            print('    params', params)

            if params.get('program_studi') != 'GENERAL':
                if params.get('kode'):
                    res = self.connection.find_one(db_courses, {'kode': params['kode']})
                    if (res['status'] == False and res['data'] == None):
                        raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' tidak ditemukan!' })
                    
                    if params.get('nama'):
                        if params.get('sks_akademik') and params.get('sks_bayar'):
                            params.update({'prodi': session['user']['prodi']})
                            res = self.connection.update_one(db_courses, {'kode': params['kode']}, params)
                            if res['status'] == False:
                                raise CustomError({ 'message': res['message'] })
                            else:
                                result.update({ 'message': res['message'] })
                        else:
                            raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
                    else:
                        raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
                else:
                    raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })
            else:
                raise CustomError({ 'message': 'Matkul ini tidak bisa diedit!' })
                    
            result.update({ 'status': True })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        print('    result', result)
        return result
    
    def func(self):
        result = { 'status': False }
        print('  [ DAO ] func')
        
        try:
            result.update({ 'status': True })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def delete_matkul(self, params: dict):
        result = { 'status': False }
        print('  [ DAO ] delete matkul')

        try:
            program_studi = list({item["program_studi"] for item in params})
            if 'GENERAL' in program_studi:
                raise CustomError({ 'message': 'Matkul ' + [item.get('kode') for item in params if item["program_studi"] == "GENERAL"] + ' tidak bisa dihapus!' })
                
            list_kode = [item["kode"] for item in params]
            print('  list_kode', list_kode, params)
            res = self.connection.delete_many(
                db_courses, 
                { 
                    'kode' : { '$in': list_kode }, 
                    'program_studi': session['user']['prodi'] 
                }
            )
            if res['status'] == False:
                raise CustomError({ 'message': res['message'] })
            else:
                result.update({ 'status': True, 'message': res['message'] })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
        except Exception as e:
            print(f'[ ERROR ] delete matkul: {e}')
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result