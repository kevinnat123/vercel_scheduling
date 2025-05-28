from dao import Database
from config import MONGO_DB, MONGO_COURSES_COLLECTION as db_courses, MONGO_OPEN_COURSES_COLLECTION as db_open_courses
from flask import session

class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

class mataKuliahPilihanDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_lovMatkul(self):
        print(f"{'':<5}{'[ DAO ]':<10} Get LOV Matkul (Prodi: {session['user']['prodi']})")
        result = self.connection.find_many(db_courses, {'prodi': { '$in' : ['GENERAL', session['user']['prodi']] }}, sort=[("kode", 1)])
        return result['data'] if result and result.get('status') else None

    def get_listMatkulTersimpan(self):
        print(f"{'':<5}{'[ DAO ]':<10} Get List Matkul Tersimpan (Prodi: {session['user']['prodi']})")
        result = self.connection.find_many(
            db_open_courses, 
            {
                'prodi': session['user']['prodi'], 
                'u_id': { "$regex": "^" + str(session['academic_details']['tahun_ajaran_1']) + str(session['academic_details']['semester_depan']) }
            }, 
            sort=[("angkatan", 1)] 
        )
        return result['data'] if result and result.get('status') else []

    def post_matkul(self, params):
        print(f"{'':<5}{'[ DAO ]':<10} Post Matkul (Parameter: {params})")
        result = { 'status': False }
        
        try:
            if params.get('angkatan'):
                params.update({
                    'u_id': (str(session['academic_details']['tahun_ajaran_1']) + str(session['academic_details']['semester_depan']) + str(params['angkatan'])).upper(),
                    'prodi': session['user']['prodi']
                })

                res = self.connection.find_one(db_open_courses, {'u_id': params['u_id']})
                if (res['status'] == True):
                    raise CustomError({ 'message': 'Data matkul untuk angkatan ' + str(params['angkatan']) + ' sudah ada!' })
                
                if params.get('jumlah_mahasiswa') or params.get('angkatan') == 'ALL':
                    if params.get('list_matkul'):
                        res = self.connection.insert_one(db_open_courses, params)
                        if res['status'] == False:
                            raise CustomError({ 'message': res['message'] })
                        else:
                            result.update({ 'message': res['message'], 'data': params['u_id'] })
                    else:
                        raise CustomError({ 'message': 'Belum ada matkul yang dibuka untuk semester ini!', 'target': 'input_matkul' })
                else:
                    raise CustomError({ 'message': 'Jumlah Mahasiswa Aktif belum diisi!', 'target': 'input_mhsAktif' })
            else:
                raise CustomError({ 'message': 'Input Angkatan belum diisi!', 'target': 'input_angkatan' })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def put_matkul(self, params):
        print(f"{'':<5}{'[ DAO ]':<10} Put Matkul (Parameter: {params})")
        result = { 'status': False }
        
        try:
            if params.get('angkatan'):
                params.update({
                    'u_id': (str(session['academic_details']['tahun_ajaran_1']) + str(session['academic_details']['semester_depan']) + str(params['angkatan'])).upper(),
                    'prodi': session['user']['prodi']
                })

                res = self.connection.find_one(db_open_courses, {'u_id': params['u_id']})
                print(f"{'':<15} Found ? {res}")
                if (res['status'] == False):
                    raise CustomError({ 'message': 'Data matkul untuk angkatan ' + str(params['angkatan']) + ' belum ada!' })
                
                if params.get('jumlah_mahasiswa') or params.get('angkatan') == 'ALL':
                    if params.get('list_matkul'):
                        res = self.connection.update_one(db_open_courses, {'u_id': params['u_id'], 'prodi': params['prodi']}, params)
                        print(f"{'':<15} Update Result: {res}")
                        if res['status'] == False:
                            raise CustomError({ 'message': res['message'] })
                        else:
                            result.update({ 'message': res['message'], 'data': params['u_id'] })
                    else:
                        raise CustomError({ 'message': 'Belum ada matkul yang dibuka untuk semester ini!', 'target': 'input_matkul' })
                else:
                    raise CustomError({ 'message': 'Jumlah Mahasiswa Aktif belum diisi!', 'target': 'input_mhsAktif' })
            else:
                raise CustomError({ 'message': 'Input Angkatan belum diisi!', 'target': 'input_angkatan' })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result
    
    def delete_data(self, req):
        print(f"{'':<5}{'[ DAO ]':<10} Delete Matkul (Parameter: {req})")
        result = { 'status': False }
        
        try:
            res = self.connection.delete_one(db_open_courses, {'u_id': req[5::].upper()})
            if res['status'] == False:
                raise CustomError({ 'message': res['message'] })
            else:
                result.update({ 'message': res['message'] })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result