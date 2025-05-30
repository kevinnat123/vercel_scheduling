from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_URLS_COLLECTION as db_urls
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

class loginDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def signUp(self, u_id, role, password):
        print(f"{'':<7}{'[ DAO ]':<8} Sign Up User: {u_id}")
        # # PYTHON 3.7.9 (Method Hash: "pbkdf2:sha256")
        # result = self.connection.insert_one(db_users, {'u_id': u_id, 'role': 'ADMIN', 'password': generate_password_hash(password, method='pbkdf2:sha256')})
        # DEFAULT HASH: "scrypt"
        result = self.connection.insert_one(db_users, {'u_id': u_id, 'role': role.upper(), 'password': generate_password_hash(password)}, True)
        return result
    
    def get_user_id(self, u_id):
        print(f"{'':<7}{'[ DAO ]':<8} Get User ID: {u_id}")
        result = self.connection.find_one(db_users, {"u_id": u_id.upper()})
        return result['data']['u_id'] if result and result.get('status') else None

    def get_user(self, u_id):
        print(f"{'':<7}{'[ DAO ]':<8} Get User: {u_id}")
        result = self.connection.find_one(db_users, {"u_id": u_id.upper()})
        return result if result and result.get('status') else None
    
    def get_menu(self, role):
        print(f"{'':<7}{'[ DAO ]':<8} get menu: {role}")
        general_menu = self.connection.find_many(db_urls, {"role": "GENERAL"})
        user_menu = self.connection.find_many(db_urls, {"role": role})
        if general_menu and general_menu.get('status'):
            if user_menu and user_menu.get('status'):
                for x in user_menu['data']:
                    general_menu['data'].append(x)
            for x in general_menu['data']:
                print(f"{'':<15} General Menu {x}")
                del x['role']
            return general_menu['data'] if general_menu['data'] else None
        return None

    def verify_user(self, u_id, password):
        print(f"{'':<7}{'[ DAO ]':<8} Verify User: {u_id}, {password}")
        user = self.get_user(u_id)
        print(f"{'':<15} User: {user}")
        if user:
            user_data = user['data']
            stored_password = user_data.get('password', '')
            print(f"{'':<15} stored_password      : {type(stored_password)}, {stored_password}")
            print(f"{'':<15} password param       : {type(password)}, {password}")
            print(f"{'':<15} check_password_hash  : {check_password_hash(stored_password, password)}")
            if check_password_hash(stored_password, password):
                del user_data['password']
                session['user'] = user['data']
                return {'status': True, 'data': user_data, 'message': 'Login berhasil'}
        return {'status': False, 'message': 'NIP atau password salah'}