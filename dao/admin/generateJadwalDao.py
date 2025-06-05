from dao import Database
from config import MONGO_DB, MONGO_LECTURERS_COLLECTION as db_dosen, MONGO_OPEN_COURSES_COLLECTION as db_matkul, MONGO_CLASSES_COLLECTION as db_kelas
from config import MONGO_SCHEDULE_COLLECTION as db_jadwal
from flask import session

class CustomError(Exception):
    def __init__(self, error_dict):
        self.error_dict = error_dict
        super().__init__(str(error_dict))

class generateJadwalDao:
    def __init__(self):
        self.connection = Database(MONGO_DB)

    def get_dosen(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Dosen")
        result = self.connection.find_many(db_dosen)
        return result['data'] if result and result.get('status') else []
    
    def get_open_matkul(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get Matkul")
        result = self.connection.find_many(db_matkul, {'u_id': { "$regex": "^" + (session['academic_details']['tahun_ajaran_berikutnya'].replace("/","-") + "_" + session['academic_details']['semester_depan']).upper() }})
        if result and result.get('status'):
            resultData = [data for data in result['data']] # [ [{}], [{}] ]
            list_matkul = []
            for dt in resultData:
                for matkul in dt['list_matkul']:
                    matkul.update({'jumlah_mahasiswa': dt['jumlah_mahasiswa']})
                    list_matkul.append(matkul)
        return list_matkul if result and result.get('status') else []
    
    def get_kelas(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get kelas")
        result = self.connection.find_many(db_kelas)
        return result['data'] if result and result.get('status') else []

    def get_jadwal(self):
        print(f"{'':<7}{'[ DAO ]':<8} Get jadwal")
        u_id = str(session['academic_details']['semester_depan']) + "_" + str(session['academic_details']['tahun_ajaran_berikutnya']).replace("/", "-")
        result = self.connection.find_one(db_jadwal, {'u_id': u_id})
        return result['data'] if result and result.get('status') else []
    
    def upload_jadwal(self, jadwal):
        print(f"{'':<7}{'[ DAO ]':<8} Upload Jadwal")
        result = { 'status': False }

        try:
            u_id = str(session['academic_details']['semester_depan']) + "_" + str(session['academic_details']['tahun_ajaran_berikutnya']).replace("/", "-")
            res = self.connection.find_one(db_jadwal, {'u_id': u_id})
            data = {
                "u_id": u_id,
                "jadwal": jadwal
            }
            if (res['status'] == True):
                if session['user']['role'] == "ADMIN":
                    res = self.connection.update_one(db_jadwal, {'u_id': data['u_id']}, data)

                    if res['status'] == True:
                        result.update({ 'message': 'Jadwal untuk semester ' + session['academic_details']['semester_depan'] + ' tahun ajaran ' + session['academic_details']['tahun_ajaran_berikutnya'] + ' berhasil diperbaharui!' })
                    else:
                        raise CustomError({ 'message': res['message'] })
            else:
                if session['user']['role'] == "ADMIN":
                    res = self.connection.insert_one(db_jadwal, data)

                    if res['status'] == True:
                        result.update({ 'message': 'Jadwal untuk semester ' + session['academic_details']['semester_depan'] + ' tahun ajaran ' + session['academic_details']['tahun_ajaran_berikutnya'] + ' berhasil ditambahkan!' })
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