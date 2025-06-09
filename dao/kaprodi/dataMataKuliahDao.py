from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_COURSES_COLLECTION as db_matkul, MONGO_LECTURERS_COLLECTION as db_dosen
from flask import session

from global_func import CustomError

class dataMataKuliahDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def put_kelompok(self, nama_baru):
        print(f"{'':<7}{'[ DAO ]':<8} Put Kelompok (Data Baru: {nama_baru})")
        result = { 'status': False }
        try:
            if nama_baru.upper() in session['user']['kelompok_matkul']:
                raise CustomError({ 'message': 'Kelompok dengan nama ' + nama_baru.upper() + ' sudah ada!' })

            session['user']['kelompok_matkul'].extend([nama_baru.upper()])
            result = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'kelompok_matkul': session['user']['kelompok_matkul']})
            if result and result.get('status') == False:
                session['user']['kelompok_matkul'].remove(nama_baru.upper())
                raise CustomError({ 'message': result.get('message') })

            result.update({ 'status': True, 'message': result.get('message') })
        except CustomError as e:
            result.update({ "message": f"{e.error_dict.get('message')}" })
        except Exception as e:
            print(f"{'':<15} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        session.modified = True  # Pastikan perubahan tersimpan
        return result
    
    def get_matkul(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul")
        if session['user']['role'] == "KEPALA PROGRAM STUDI":
            result = self.connection.find_many(
                db_matkul, 
                {'prodi': { '$in' : [session['user']['prodi']] }}, 
                # { '$in' : ['GENERAL', session['user']['prodi']] }
                sort=[("kode", 1)]
            )
        elif session['user']['role'] == "ADMIN":
            result = self.connection.find_many(db_matkul, sort=[("prodi", 1), ("kode", 1)])
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def get_matkul_by_prodi(self, prodi=""):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul By Prodi (prodi: {prodi})")
        result = self.connection.find_many(
            db_matkul, 
            {'prodi': prodi}, 
            sort=[("kode", 1)]
        )
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def get_matkul_by_kode(self, list_kode=[]):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul By Kode (list_kode: {str(list_kode)})")
        result = self.connection.find_many(
            db_matkul, 
            { 'kode': {'$in': list_kode} }, 
            sort=[("kode", 1)]
        )
        if result and result.get('status'):
            for matkul in result['data']:
                matkul.setdefault('kelompok', None)
                matkul.setdefault('asistensi', None)
                matkul.setdefault('prodi', None)
        return result['data'] if result and result.get('status') else []
    
    def post_matkul(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Post Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
            elif not params.get('sks_akademik') or not params.get('sks_bayar'):
                raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            elif not params.get('tipe_kelas'):
                raise CustomError({ 'message': 'Tipe Kelas belum diisi!' })
            elif params.get('asistensi') and not params.get('integrated_class') and not params.get('tipe_kelas_asistensi'):
                raise CustomError({ 'message': 'Tipe Kelas Asistensi belum diisi!' })
            elif params.get('team_teaching') and not params.get('jumlah_dosen'):
                raise CustomError({ 'message': 'Jumlah Dosen Pengajar belum diisi!' })

            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })

            # Hapus key yang memiliki value kosong
            if not params.get('asistensi'):
                if 'asistensi' in params: params.pop('asistensi')
                if 'tipe_kelas_asistensi' in params: params.pop('tipe_kelas_asistensi')
                if 'integrated_class' in params: params.pop('integrated_class')
            else:
                if params.get('integrated_class'):
                    if 'tipe_kelas_asistensi' in params: params.pop('tipe_kelas_asistensi')
            if not params.get('team_teaching'):
                if 'team_teaching' in params: params.pop('team_teaching')
                if 'jumlah_dosen' in params: params.pop('jumlah_dosen')
            params = {k: v for k, v in params.items() if v}

            # Check exist
            res = self.connection.find_one(db_matkul, {'kode': params['kode']})
            if (res['status'] == True):
                raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' sudah ada!' })

            # Update Dosen
            if params.get('dosen_ajar'):
                for dosen in params['dosen_ajar']:
                    data_dosen = self.connection.find_one(db_dosen, {'nama': dosen})
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data'].get('matkul_ajar') or []
                        if params['nama'] not in data_dosen:
                            data_dosen.append(params['nama'])
                            self.connection.update_one(db_dosen, {'nama': dosen}, {'matkul_ajar': data_dosen})

            res = self.connection.insert_one(db_matkul, params)
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

        print(f"{'':<15} Result: {result}")
        return result
    
    def put_matkul(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Put Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            if not params.get('kode'):
                raise CustomError({ 'message': 'Kode Matkul belum diisi!', 'target': 'input_kode' })
            elif not params.get('nama'):
                raise CustomError({ 'message': 'Nama Matkul belum diisi!', 'target': 'input_nama' })
            elif not params.get('sks_akademik') or not params.get('sks_bayar'):
                raise CustomError({ 'message': 'SKS Akademik / Bayar belum diisi!', 'target': 'input_sksA' if not params.get('sks_akademik') else 'input_sksB' })
            elif not params.get('prodi'):
                raise CustomError({ 'message': 'Program Studi belum diisi!' })
            elif not params.get('tipe_kelas'):
                raise CustomError({ 'message': 'Tipe Kelas belum diisi!' })
            elif params.get('asistensi') and not params.get('integrated_class') and not params.get('tipe_kelas_asistensi'):
                raise CustomError({ 'message': 'Tipe Kelas Asistensi belum diisi!' })
            elif params.get('team_teaching') and not params.get('jumlah_dosen'):
                raise CustomError({ 'message': 'Jumlah Dosen Pengajar belum diisi!' })
                
            if session['user']['role'] == "KEPALA PROGRAM STUDI":
                if params['prodi'] != session['user']['prodi']:
                    raise CustomError({ 'message': 'Anda input program studi diluar program studi anda! (Input Anda: ' + params['prodi'] + ')' })
                
            matkul_exist = self.connection.find_one(db_matkul, {'kode': params['kode']})
            if (matkul_exist['status'] == False and matkul_exist['data'] == None):
                raise CustomError({ 'message': 'Data dengan Kode Matkul ' + params['kode'] + ' tidak ditemukan!' })
            
            # Hapus key yang memiliki value kosong
            unset = {k: "" for k, v in params.items() if not v}
            if not params.get('asistensi'):
                if 'asistensi' in params: params.pop('asistensi')
                if 'tipe_kelas_asistensi' in params: params.pop('tipe_kelas_asistensi')
                if 'integrated_class' in params: params.pop('integrated_class')

                if 'asistensi' not in unset: unset['asistensi'] = ''
                if 'tipe_kelas_asistensi' not in unset: unset['tipe_kelas_asistensi'] = ''
                if 'integrated_class' not in unset: unset['integrated_class'] = ''
            else:
                if params.get('integrated_class'):
                    if 'tipe_kelas_asistensi' in params: 
                        unset['tipe_kelas_asistensi'] = ""
                        params.pop('tipe_kelas_asistensi')
            if not params.get('team_teaching'):
                if 'team_teaching' in params: params.pop('team_teaching')
                if 'jumlah_dosen' in params: params.pop('jumlah_dosen')
                
                if 'team_teaching' not in unset: unset['team_teaching'] = ''
                if 'jumlah_dosen' not in unset: unset['jumlah_dosen'] = ''
            params = {k: v for k, v in params.items() if v}
            
            res = self.connection.update_one(db_matkul, {'kode': params['kode']}, params, unset)

            # Update Dosen
            if params.get('dosen_ajar'):
                for dosen in params['dosen_ajar']:
                    data_dosen = self.connection.find_one(db_dosen, {'nama': dosen})
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data'].get('matkul_ajar') or []
                        if params['nama'] not in data_dosen:
                            data_dosen.append(params['nama'])
                            self.connection.update_one(db_dosen, {'nama': dosen}, {'matkul_ajar': data_dosen})
                    else:
                        raise Exception

            if len(params.get('dosen_ajar') or []) < len(matkul_exist['data'].get('dosen_ajar') or []):
                dosen_ajar_lama = matkul_exist['data'].get('dosen_ajar') or []
                dosen_ajar_baru = params.get('dosen_ajar') or []
                data_dihapus = [dt for dt in dosen_ajar_lama if dt not in dosen_ajar_baru]

                for dosen in data_dihapus:
                    data_dosen = self.connection.find_one(db_dosen, {'nama': dosen})
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data']
                        data_dosen['matkul_ajar'].remove(params['nama'])
                        if data_dosen['matkul_ajar']:
                            self.connection.update_one(db_dosen, {'nama': dosen}, {'matkul_ajar': data_dosen["matkul_ajar"]})
                        else:
                            self.connection.update_one(db_dosen, {'nama': dosen}, {}, {'matkul_ajar': ''})
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

        print(f"{'':<15} Result: {result}")
        return result
    
    def delete_matkul(self, params: dict):
        print(f"{'':<7}{'[ DAO ]':<8} Delete Matkul (Parameter: {params})")
        result = { 'status': False }

        try:
            params = self.connection.find_many(
                db_matkul, 
                {'kode': { '$in' : [item['kode'] for item in params] }}, 
                sort=[("kode", 1)]
            )
            if params and params.get('status'):
                params = params['data']
                list_kode = [item["kode"] for item in params]
                list_prodi = [item["prodi"] for item in params]
            else:
                raise Exception
            
            if session['user']['role'] == "KAPRODI":
                if any(prodi != session['user']['prodi'] for prodi in list_prodi):
                    raise CustomError({ 'message': 'Anda mengubah program studi diluar program studi anda! (Input Anda: ' + str([prodi for prodi in list_prodi if prodi != session['user']['prodi']]) + ')' })
                if 'GENERAL' in list_prodi:
                    raise CustomError({ 'message': 'Matkul ' + [item.get('kode') for item in params if item["prodi"] == "GENERAL"] + ' tidak bisa dihapus!' })
            
            for matkul in params:
                dosen_ajar_matkul = matkul.get('dosen_ajar') or []
                for dosen in dosen_ajar_matkul:
                    data_dosen = self.connection.find_one(db_dosen, {'nama': dosen})
                    if data_dosen and data_dosen.get('status'):
                        data_dosen = data_dosen['data']
                        data_dosen['matkul_ajar'].remove(matkul['nama'])
                        if data_dosen['matkul_ajar']:
                            self.connection.update_one(db_dosen, {'nama': dosen}, {'matkul_ajar': data_dosen['matkul_ajar']})
                        else:
                            self.connection.update_one(db_dosen, {'nama': dosen}, {}, {'matkul_ajar': ""})
                    else:
                        raise Exception
            
            res = self.connection.delete_many(
                db_matkul, 
                { 
                    'kode' : { '$in': list_kode }, 
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