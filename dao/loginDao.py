from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users
from werkzeug.security import check_password_hash, generate_password_hash

class loginDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def signUp(self, username, password):
        print('  [ DAO ] sign up user', username)
        result = self.connection.insert_one(db_users, {'Username': username, 'Role': 'Admin', 'Password': generate_password_hash(password)})
        return result

    def get_user(self, username):
        print('  [ DAO ] get user', username)
        result = self.connection.find_one(db_users, {"Username": username})
        return result if result and result.get('status') else None

    def verify_user(self, username, password):
        print('  [ DAO ] verify user', username, password)
        user = self.get_user(username)
        print('    user', user) 
        if user:
            user_data = user['data']
            stored_password = user_data.get('Password', '')
            print('    stored_password      :', type(stored_password), stored_password)
            print('    password param       :', type(password), password)
            print('    check_password_hash  :', check_password_hash(stored_password, password))
            if check_password_hash(stored_password, password):
                del user_data['Password']
                return {'status': True, 'data': user_data, 'message': 'Login berhasil'}
        return {'status': False, 'message': 'Username atau password salah'}
