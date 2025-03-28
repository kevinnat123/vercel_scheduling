from dao import Database
from config import MONGO_DB, MONGO_USERS_COLLECTION as db_users

# Fungsi untuk mengambil data (contoh data dummy)
class First:
    def __init__(self):
        self.connection = Database(MONGO_DB)
    
    def get_data(self):
        result = {'status': False, 'data': None, 'message': ''}
        print('get_data()')
        try:
            collection = self.connection.find_all(collection_name=db_users)
            print('collection', collection)
            result['status'] = True
            result['data'] = collection
            result['message'] = 'Data berhasil diambil'
        except Exception as e:
            result['message'] = f'Error: {str(e)}'

        return result
