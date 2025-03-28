from pymongo import MongoClient, errors
import config

class Database:
    def __init__(self, dbname):
        try:
            self.connection = MongoClient(config.MONGO_URI)
            self.db = self.connection[dbname]
        except errors.ConnectionFailure as conn_fail:
            print(f"Gagal Membuat Koneksi | {conn_fail}")
        except Exception as err:
            print(f"Gagal membuat koneksi (Others) | {err}")

    def get_collection(self, collection_name):
        return self.db[collection_name]
    
    def ambil_data(self, collection_name):
        print('ambil_data')
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.get_collection(collection_name)
            print('col', collection)
            resultFind = collection.find()
            if resultFind:
                data_list = []

                for doc in resultFind:
                    doc['_id'] = str(doc['_id'])  # Ubah ObjectId ke string
                    data_list.append(doc)
                    
                result['status'] = True
                result['data'] = resultFind
                result['message'] = 'Data ditemukan'
            else:
                result['message'] = 'Data tidak ditemukan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat mengambil data'

        return result

    def find_one(self, collection_name, filter):
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.get_collection(collection_name)
            resultFind = collection.find_one(filter)
            if resultFind:
                resultFind['_id'] = str(resultFind['_id']) 
                result['status'] = True
                result['data'] = resultFind
                result['message'] = 'Data ditemukan'
            else:
                result['message'] = 'Data tidak ditemukan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat mengambil data'

        return result

    def find_all(self, collection_name, page=1, per_page=10, search_query=None, search_field=None, sort=None):
        result = {'status': False, 'data': None, 'message': '', 'total_documents': 0}
        
        try:
            collection = self.get_collection(collection_name)
            filter = {}

            if search_query and search_field:
                filter = {search_field: {'$regex': search_query, '$options': 'i'}}

            total_documents = collection.count_documents(filter)
            cursor = collection.find(filter)

            if sort:
                cursor = cursor.sort(sort)

            data = []
            for document in cursor.skip((page - 1) * per_page).limit(per_page):
                document['_id'] = str(document['_id'])  # Konversi ObjectId ke string
                data.append(document)

            result['status'] = True
            result['data'] = data
            result['message'] = 'Data ditemukan'
            result['total_documents'] = total_documents

            # Konversi ObjectId ke string
            for item in result['data']:
                item['_id'] = str(item['_id'])

            # Fitur pencarian
            if search_query and search_field:
                result['data'] = [item for item in result['data'] if search_query.lower() in item.get(search_field, '').lower()]

            # Pengaturan halaman dan jumlah data per halaman
            total_documents = len(result['data'])
            start_index = (page - 1) * per_page
            end_index = start_index + per_page
            result['data'] = result['data'][start_index:end_index]
            result['total_documents'] = total_documents
            
        except errors.PyMongoError as e:
            print(f"Error pymongo : {e}")
            result['message'] = 'Terjadi kesalahan saat mengambil data'

        except Exception as e:
            print(f'Terjadi kesalahan: {str(e)}')
            result['message'] = f'Terjadi kesalahan: {str(e)}'

        return result  # Menggunakan jsonify untuk mengonversi dictionary ke JSON

    def findMany(self, collection_name, filter):
        status = False
        data = None
        try:
            collection = self.db[collection_name]
            resultFind = collection.find(filter)
            data = list(resultFind)
            status = True
        except errors.PyMongoError as pymongoError:
            print(f"Gagal find many data, error pymongo: {pymongoError}")
        except Exception as err:
            print(f"Gagal find many data, other error: {err}")
        return status, data

    def insert_one(self, collection_name, data):
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.db[collection_name]
            insertResult = collection.insert_one(data)
            result['status'] = True
            result['data'] = {'inserted_id': str(insertResult.inserted_id)}
            result['message'] = 'Data berhasil ditambahkan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat menambahkan data'

        return result
    
    def insert_many(self, collection_name, data):
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.db[collection_name]
            insertResult = collection.insert_many(data)
            result['status'] = True
            result['data'] = {'inserted_ids': [str(id) for id in insertResult.inserted_ids]}
            result['message'] = 'Data berhasil ditambahkan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat menambahkan data'

        return result


    def update_one(self, collection_name, filter, data):
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.db[collection_name]
            updateResult = collection.update_one(filter, {'$set': data})
            if updateResult.modified_count > 0:
                result['status'] = True
                result['message'] = 'Data berhasil diperbarui'
            else:
                result['message'] = 'Data tidak ditemukan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat memperbarui data'

        return result

    def delete_one(self, collection_name, filter):
        result = {'status': False, 'data': None, 'message': ''}
        try:
            collection = self.db[collection_name]
            deleteResult = collection.delete_one(filter)
            if deleteResult.deleted_count > 0:
                result['status'] = True
                result['message'] = 'Data berhasil dihapus'
            else:
                result['message'] = 'Data tidak ditemukan'
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            result['message'] = 'Terjadi kesalahan saat menghapus data'

        return result
    
    def count_documents(self, collection_name, filter={}):
        try:
            collection = self.get_collection(collection_name)
            return collection.count_documents(filter)
        except errors.PyMongoError as pymongoError:
            print(f"Error pymongo : {pymongoError}")
            return 0

    def __del__(self):
        self.connection.close()
