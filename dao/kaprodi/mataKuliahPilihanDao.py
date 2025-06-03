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
        print(f"{'':<7}{'[ DAO ]':<8} Get LOV Matkul (Prodi: {session['user']['prodi']})")
        result = self.connection.find_many(db_courses, {'prodi': { '$in' : ['GENERAL', session['user']['prodi']] }}, sort=[("kode", 1)])
        return result['data'] if result and result.get('status') else None

    def get_listMatkulTersimpan(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get List Matkul Tersimpan (Prodi: {session['user']['prodi']})")
        result = self.connection.find_many(
            db_open_courses, 
            {
                '$and': [
                    {'prodi': session['user']['prodi']}, 
                    {'u_id': { "$regex": "^" + (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper() }}
                ]
            }, 
            sort=[("angkatan", 1)] 
        )
        print('result', result)
        return result['data'] if result and result.get('status') else []

    def post_matkul(self, params):
        print(f"{'':<7}{'[ DAO ]':<8} Post Matkul (Parameter: {params})")
        result = { 'status': False }
        
        try:
            if not params.get('angkatan'):
               raise CustomError({ 'message': 'Input Angkatan belum diisi!', 'target': 'input_angkatan' })
            if not params.get('jumlah_mahasiswa') and not params.get('angkatan') == 'ALL':
                raise CustomError({ 'message': 'Jumlah Mahasiswa Aktif belum diisi!', 'target': 'input_mhsAktif' })
            if not params.get('list_matkul'):
                raise CustomError({ 'message': 'Belum ada matkul yang dibuka untuk semester ini!', 'target': 'input_matkul' })

            params = {k: v for k, v in params.items() if v}

            u_id = (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper()
            u_id = u_id + ("_" + params['bidang_minat'].replace(" ", "_") if params.get('bidang_minat') else '') + "_" + str(params['angkatan'])
            params.update({
                'u_id': u_id,
                'prodi': session['user']['prodi']
            })

            res = self.connection.find_one(db_open_courses, {'u_id': params['u_id']})
            if (res['status'] == True):
                if not params.get('bidang_minat') and not res['data'].get('bidang_minat'):
                    raise CustomError({ 'message': f"Data matkul untuk angkatan {params['angkatan']} sudah ada!" })
                elif params.get('bidang_minat') and (params['bidang_minat'] == res['data'].get('bidang_minat')):
                    raise CustomError({ 'message': f"Data matkul untuk angkatan {params['angkatan']} dengan bidang minat {params['bidang_minat']} sudah ada!" })
            
            res = self.connection.insert_one(db_open_courses, params)
            if res['status'] == True:
                result.update({ 'message': res['message'], 'data': params['u_id'] })
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
        print(f"{'':<15} {result}")
        return result
    
    def put_matkul(self, params):
        print(f"{'':<7}{'[ DAO ]':<8} Put Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('angkatan'):
                raise CustomError({ 'message': 'Input Angkatan belum diisi!', 'target': 'input_angkatan' })
            if not params.get('jumlah_mahasiswa') and not params.get('angkatan') == 'ALL':
                raise CustomError({ 'message': 'Jumlah Mahasiswa Aktif belum diisi!', 'target': 'input_mhsAktif' })
            if not params.get('list_matkul'):
                raise CustomError({ 'message': 'Belum ada matkul yang dibuka untuk semester ini!', 'target': 'input_matkul' })

            params = {k: v for k, v in params.items() if v}

            u_id = (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper()
            u_id = u_id + ("_" + params['bidang_minat'].replace(" ", "_") if params.get('bidang_minat') else '') + "_" + str(params['angkatan'])
            params.update({
                'u_id': u_id,
                'prodi': session['user']['prodi']
            })

            res = self.connection.find_one(db_open_courses, {'u_id': params['u_id']})
            if (res['status'] == True):
                # CODE BAGIAN INI MEMUSINGKAN T_T
                if res['data']['u_id'] != u_id and params['angkatan'] == res['data']['angkatan']:
                    if not params.get('bidang_minat') and not res['data'].get('bidang_minat'):
                        raise CustomError({ 'message': f"Data matkul untuk angkatan {params['angkatan']} sudah ada!" })
                    elif params.get('bidang_minat') and (params['bidang_minat'] == res['data'].get('bidang_minat')):
                        raise CustomError({ 'message': f"Data matkul untuk angkatan {params['angkatan']} dengan bidang minat {params['bidang_minat']} sudah ada!" })
            elif (res['status'] == False):
                raise CustomError({ 'message': 'Data matkul untuk angkatan ' + str(params['angkatan']) + ' belum ada!' })
            
            res = self.connection.update_one(db_open_courses, {'u_id': params['u_id'], 'prodi': params['prodi']}, params)
            print(f"{'':<15} Update Result: {res}")
            if res['status'] == False:
                raise CustomError({ 'message': res['message'] })
            else:
                result.update({ 'message': res['message'], 'data': params['u_id'] })

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
        print(f"{'':<7}{'[ DAO ]':<8} Delete Matkul (Parameter: {req}; {req[5:]})")
        result = { 'status': False }
        
        try:
            res = self.connection.delete_one(db_open_courses, {'u_id': req[5:].upper()})
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