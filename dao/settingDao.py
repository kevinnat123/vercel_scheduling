from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

class settingDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_user(self, u_id):
        print('  [ DAO ] get user', u_id)
        # print('  [ generate "kaprodi" ]', generate_password_hash('kaprodi'))
        result = self.connection.find_one(db_users, {"u_id": u_id.upper()})
        return result if result and result.get('status') else None

    def register_new_password(self, oldPassword, newPassword, verifyNewPassword):
        print('  [ DAO ] register new password', oldPassword, newPassword, verifyNewPassword)
        user = self.get_user(session['user']['u_id'])
        if user:
            user_data = user['data']
            stored_password = user_data.get('password', '')
            if check_password_hash(stored_password, oldPassword):
                del user_data['password']
                if (oldPassword == newPassword):
                    return {'status': False, 'message': 'Silahkan masukkan password yang berbeda!'}
                
                if (newPassword == verifyNewPassword):
                    print('   GENERATOR', generate_password_hash(newPassword))
                    register_user_password = self.connection.update_one(
                        db_users, 
                        { 'u_id': session['user']['u_id'] }, 
                        { 'password': generate_password_hash(newPassword) },
                        sensitive= True
                    )
                    if register_user_password and register_user_password['status']:
                        return {'status': True, 'message': 'Password berhasil disimpan!'}
                else:
                    return {'status': False, 'message': 'Input password baru tidak cocok!'}
        return {'status': False, 'message': 'NIP atau password salah'}
    
    def update_general(self, params):
        print('  [ DAO ] update general', params)
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
        print('  [ DAO ] update kelompok matkul', data)

        if data:
            newGroup = [item["kelompok_matkul"] for item in data]
            print(newGroup)
            updateData = self.connection.update_one(db_users, {'u_id': session['user']['u_id']}, {'kelompok_matkul': newGroup})
            
            if updateData and updateData['status']:
                session['user']['kelompok_matkul'] = newGroup
                session.modified = True

            return {'status': updateData.get('status'), 'message': updateData.get('message')}
        
        return {'status': False, 'message': 'Data tidak valid'}