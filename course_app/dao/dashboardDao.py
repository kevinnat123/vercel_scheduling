from course_app.dao import Database
from course_app.mongoConfig import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_MAJOR_COLLECTION as db_prodi
from flask import session
from course_app.global_func import CustomError

class dashboardDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_user(self, u_id=None, prodi=None):
        print(f"{'[ DAO ]':<25} Get User (u_id: {u_id})")
        if u_id:
            result = self.connection.find_one(
                collection_name = db_users, 
                filter          = {"u_id": u_id.upper()}
            )
        elif prodi:
            result = self.connection.find_one(
                collection_name = db_users, 
                filter          = {'prodi': prodi}
            )
        return result if result and result.get('status') else None

    def update_general(self, params):
        print(f"{'[ DAO ]':<25} Update General (Parameter: {params})")
        result = { 'status': False }

        try:
            if session['user']['role'] in ["KEPALA PROGRAM STUDI"]:
                if params.get('maks_sks'):
                    if params['maks_sks'] > 50:
                        raise CustomError({ 'message': 'Beban SKS terlalu banyak!' })
                    
                    res = self.connection.update_one(
                        collection_name = db_prodi,
                        filter          = { 'program_studi': session['user']['prodi'] },
                        update_data     = { 'maks_sks': params['maks_sks'] }
                    )

                    if res['status'] == True:
                        result.update({ 'message': res['message'] })
                    else:
                        raise CustomError({ 'message': res['message'] })
                else:
                    raise CustomError({ 'message': 'Tidak ada yang perlu disimpan'})
            else:
                raise CustomError({ 'message': 'Akses SKS maksimum hanya bisa diakses kaprodi!' })
            
            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })
        print(f"{'':<25} {result}")
        return result
    
    def update_kelompokMatkul(self, data):
        print(f"{'[ DAO ]':<25} Update Kelompok Matkul (Parameter: {data})")
        result = { 'status': False }

        try:
            if session['user']['role'] in ["KEPALA PROGRAM STUDI"]:
                if data:
                    newGroup = [item["kelompok_matkul"] for item in data if item['kelompok_matkul']]
                elif data == []:
                    newGroup = data
                else:
                    raise CustomError({ 'message': 'Data tidak valid' })

                res = self.connection.update_one(
                    collection_name = db_prodi, 
                    filter          = { 'program_studi': session['user']['prodi'] }, 
                    update_data     = { 'kelompok_matkul': newGroup }
                )

                if res['status'] == True:
                    result.update({ 'message': res['message'] })
                else:
                    raise CustomError({ 'message': res['message'] })
            else:
                raise CustomError({ 'message': 'Kelompok Matkul hanya bisa diakses kaprodi!' })
            
            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })
        print(f"{'':<25} {result}")
        return result
    
    def update_bidangMinat(self, data):
        print(f"{'[ DAO ]':<25} Update Bidang Minat (Parameter: {data})")
        result = { 'status': False }

        try:
            if session['user']['role'] in ["KEPALA PROGRAM STUDI"]:
                if data:
                    newGroup = [item["bidang_minat"] for item in data if item['bidang_minat']]
                elif data == []:
                    newGroup = data
                else:
                    raise CustomError({ 'message': 'Data tidak valid' })

                res = self.connection.update_one(
                    collection_name = db_prodi, 
                    filter          = { 'program_studi': session['user']['prodi'] }, 
                    update_data     = { 'bidang_minat': newGroup }
                )

                if res['status'] == True:
                    result.update({ 'message': res['message'] })
                else:
                    raise CustomError({ 'message': res['message'] })
            else:
                raise CustomError({ 'message': 'Bidang Minat prodi hanya bisa diakses kaprodi!' })
            result.update({ 'status': True })
        except CustomError as e:
            result.update( e.error_dict )
        except Exception as e:
            print(f"{'':<25} Error: {e}")
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })
        print(f"{'':<25} {result}")
        return result
    
    def update_os(self, data):
        print(f"{'[ DAO ]':<25} Update OS (Parameter: {data})")
        
        if data:
            newGroup = [item["os"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(
            collection_name = db_users, 
            filter          = {'u_id': session['user']['u_id']}, 
            update_data     = {'list_os': newGroup}
        )
        
        if updateData and updateData['status']:
            session['user']['list_os'] = newGroup
            session.modified = True

        return {'status': updateData.get('status'), 'message': updateData.get('message')}
        
    def update_processor(self, data):
        print(f"{'[ DAO ]':<25} Update Processor (Parameter: {data})")

        if data:
            newGroup = [item["processor"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(
            collection_name = db_users, 
            filter          = {'u_id': session['user']['u_id']}, 
            update_data     = {'list_processor': newGroup}
        )
        
        if updateData and updateData['status']:
            session['user']['list_processor'] = newGroup
            session.modified = True

        return {'status': updateData.get('status'), 'message': updateData.get('message')}
    
    def update_prodi(self, data):
        print(f"{'[ DAO ]':<25} Update Prodi (Parameter: {data})")
        
        if data:
            newGroup = [item["prodi"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(
            collection_name = db_users, 
            filter          = {'u_id': session['user']['u_id']}, 
            update_data     = {'list_prodi': newGroup}
        )
        
        if updateData and updateData['status']:
            session['user']['list_prodi'] = newGroup
            session.modified = True

        return {'status': updateData.get('status'), 'message': updateData.get('message')}