from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users
from flask import session

class dashboardDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_user(self, u_id=None, prodi=None):
        print(f"{'[ DAO ]':<25} Get User (u_id: {u_id})")
        if u_id:
            result = self.connection.find_one(db_users, {"u_id": u_id.upper()})
        elif prodi:
            result = self.connection.find_one(db_users, {'prodi': prodi})
        return result if result and result.get('status') else None

    def update_general(self, params):
        print(f"{'[ DAO ]':<25} Update General (Parameter: {params})")
        if params:
            user = self.get_user(session['user']['u_id'])
            if user:
                if params.get('maks_sks'):
                    if params['maks_sks'] > 50:
                        return {'status': False, 'message': 'Beban SKS terlalu banyak!'}
                    update_data = {'maks_sks_prodi': params['maks_sks']}

                result = self.connection.update_one(db_users, { 'u_id': session['user']['u_id'] }, update_data)
                if result and result.get('status') == True:
                    session['user']['maks_sks_prodi'] = params['maks_sks']
                    session.modified = True  # Pastikan perubahan tersimpan
                return {'status': result.get('status'), 'message': result.get('message')}
                
            return {'status': False, 'message': 'User Not Found'}
        return {'status': False, 'message': 'Tidak ada yang perlu disimpan'}
    
    def update_kelompokMatkul(self, data):
        print(f"{'[ DAO ]':<25} Update Kelompok Matkul (Parameter: {data})")

        if data:
            newGroup = [item["kelompok_matkul"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'kelompok_matkul': newGroup})
        
        if updateData and updateData['status']:
            session['user']['kelompok_matkul'] = newGroup
            session.modified = True
        else:
            self.connection.find_one(db_users, {'u_id': session['user']['u_id']})

        return {'status': updateData.get('status'), 'message': updateData.get('message')}
    
    def update_bidangMinat(self, data):
        print(f"{'[ DAO ]':<25} Update Bidang Minat (Parameter: {data})")

        if data:
            newGroup = [item["bidang_minat"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'bidang_minat': newGroup})

        if updateData and updateData['status']:
            session['user']['bidang_minat'] = newGroup
            session.modified = True
        else:
            self.connection.find_one(db_users, {'u_id': session['user']['u_id']})

        return {'status': updateData.get('status'), 'message': updateData.get('message')}
    
    def update_os(self, data):
        print(f"{'[ DAO ]':<25} Update OS (Parameter: {data})")
        
        if data:
            newGroup = [item["os"] for item in data]
        elif data == []:
            newGroup = data
        else:
            return {'status': False, 'message': 'Data tidak valid'}

        updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'list_os': newGroup})
        
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

        updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'list_processor': newGroup})
        
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

        updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'list_prodi': newGroup})
        
        if updateData and updateData['status']:
            session['user']['list_prodi'] = newGroup
            session.modified = True

        return {'status': updateData.get('status'), 'message': updateData.get('message')}