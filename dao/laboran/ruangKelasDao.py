from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users, MONGO_URLS_COLLECTION as db_urls
from flask import session

# if result.get('status'):
#     for y in result['data']:
#         if not y.get('konsentrasi'):
#             y.update({ 'konsentrasi': '' })

class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

class ruangKelasDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def post_kelas(self, params):
        result = { 'status': False }
        print('  [ DAO ] post kelas')
        print('    params', params)

        try:
            res = self.connection.find_many()
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
    
    

    def func(self):
        result = { 'status': False }
        print('  [ DAO ] func')
        
        try:
            res = self.connection.find_one()
            if res['status'] == False:
                raise CustomError({ 'message': res['message'] })
            else:
                result.update({ 'message': res['message'] })

            result.update({ 'status': True })
        except CustomError as e:
            result.update({ 'message': f'{e.error_dict.get('message')}' })
            if e.error_dict.get('target'):
                result.update({ 'target': e.error_dict.get('target') })
        except Exception as e:
            result.update({ 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

        return result