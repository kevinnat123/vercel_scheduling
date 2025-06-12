from dao import Database
from config import MONGO_DB, MONGO_COURSES_COLLECTION as db_courses, MONGO_OPEN_COURSES_COLLECTION as db_open_courses, MONGO_USERS_COLLECTION as db_users
from flask import session

from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
dao_matkul = dataMataKuliahDao()

from global_func import CustomError

class mataKuliahPilihanDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_listMatkulTersimpan(self, prodi=None):
        print(f"{'':<7}{'[ DAO ]':<8} Get List Matkul Tersimpan (Prodi: {prodi})")
        if prodi:
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
        else:
            result = self.connection.find_many(db_open_courses, sort=[("prodi", 1), ("angkatan", 1)] )

        if result and result.get('status'):
            for data in result['data']:
                list_kode_matkul = [matkul['kode'] for matkul in data['list_matkul']]
                list_matkul = dao_matkul.get_matkul_by_kode(list_kode_matkul)
                for matkul in list_matkul:
                    jumlah_kelas = next((data['jumlah_kelas'] for data in data['list_matkul'] if data['kode'] == matkul['kode']), None)
                    matkul['jumlah_kelas'] = jumlah_kelas
                data['list_matkul'] = [matkul for matkul in list_matkul]

        return result['data'] if result and result.get('status') else []

    def get_bidang_minat(self, prodi):
        print(f"{'':<7}{'[ DAO ]':<8} Get Bidang Minat (Prodi: {prodi})")
        result = self.connection.find_one(
            db_users, {'prodi': prodi}, 
        )
        print('result', result)
        return result['data']['bidang_minat'] if result and result.get('status') and result['data'].get('bidang_minat') else []

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

            list_matkul = params.pop('list_matkul', [])
            params['list_matkul'] = [{"kode": matkul["kode"], "jumlah_kelas": matkul["jumlah_kelas"]} for matkul in list_matkul]
            params = {k: v for k, v in params.items() if v}

            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })

            prodi_words = params['prodi'].split(' ')
            prodi = prodi_words[0]
            for w in prodi_words[1:]:
                prodi += w[0]
            if params.get('bidang_minat'):
                bidang_minat_words = params['bidang_minat'].split(' ')
                bidang_minat = ''
                for bm in bidang_minat_words:
                    bidang_minat += bm[0]
            
            u_id = (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan'] + "_" + prodi).upper()
            u_id = u_id + ("_" + bidang_minat if params.get('bidang_minat') else '') + "_" + str(params['angkatan'])
            params.update({
                'u_id': u_id,
                'prodi': params['prodi']
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

            list_matkul = params.pop('list_matkul', [])
            params['list_matkul'] = [{"kode": matkul["kode"], "jumlah_kelas": matkul["jumlah_kelas"]} for matkul in list_matkul]
            params = {k: v for k, v in params.items() if v}

            prodi_words = params['prodi'].split(' ')
            prodi = prodi_words[0]
            for w in prodi_words[1:]:
                prodi += w[0]
            if params.get('bidang_minat'):
                bidang_minat_words = params['bidang_minat'].split(' ')
                bidang_minat = ''
                for bm in bidang_minat_words:
                    bidang_minat += bm[0]
            
            u_id = (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan'] + "_" + prodi).upper()
            u_id = u_id + ("_" + bidang_minat if params.get('bidang_minat') else '') + "_" + str(params['angkatan'])
            params.update({
                'u_id': u_id,
                'prodi': params['prodi']
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