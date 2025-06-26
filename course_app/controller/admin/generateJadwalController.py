from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from course_app.dao.admin.generateJadwalDao import generateJadwalDao
from course_app.dao import genetic_algorithm as ga
from flask_login import login_required
from course_app.global_func import CustomError

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def generateJadwal_index():
    print(f"{'[ RENDER ]':<25} Generate Jadwal (Role: {session['user']['role']})")
    if session['user']['role'] != 'ADMIN':
        return redirect(url_for('signin.error403'))
    else:
        jadwal = dao.get_jadwal()
        jadwal = True if jadwal and jadwal.get('jadwal') else False
        
        return render_template(
            '/admin/generate_jadwal/index.html', 
            menu = 'Generate Jadwal', 
            title = 'Generate Jadwal', 
            semester_ajaran_depan = session['academic_details']['semester_depan'] + "_" + session['academic_details']['tahun_ajaran_berikutnya'].replace("/", "-"),
            jadwal = jadwal
        )
        
@generateJadwal.route("/generate_jadwal/generate", methods=['GET'])
@login_required
def generate_jadwal():
    print(f"{'[ CONTROLLER ]':<25} Generate Jadwal")

    try:
        if session['user']['role'] == "ADMIN":
            param = request.args.to_dict()
            regenerate = True if param['regenerate'] == 'true' else False
            
            jadwal = dao.get_jadwal()
            if jadwal and jadwal.get('jadwal') and not regenerate:
                return jsonify({ 'status': False, 'reason': 'exist'})
            
            data_dosen = dao.get_dosen()
            data_ruang = dao.get_kelas()
            data_matkul = dao.get_open_matkul()

            attempt = 1
            while attempt <= 3:
                best_schedule = ga.genetic_algorithm(
                    data_matkul, data_dosen, data_ruang, 
                    ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.05
                )
                if best_schedule and best_schedule.get('status') == True:
                    break
                attempt += 1

            if best_schedule and best_schedule.get('status') == False:
                raise CustomError({ 'message': best_schedule.get('message') })
            else:
                print("Final Schedule Fitness\n")
                ga.hitung_fitness( jadwal=best_schedule['data'], matakuliah_list=data_matkul, dosen_list=data_dosen, ruang_list=data_ruang, detail=True )
            
            # print([schedule for schedule in best_schedule['data'] if schedule['program_studi'] == 'S1 SISTEM INFORMASI'])
            dao.upload_jadwal(best_schedule['data'])
        else:
            raise CustomError({ 'message': 'Anda tidak berhak generate jadwal!\nSilahkan hubungi Admin! '})
    except CustomError as e:
        return jsonify({ 'status': False, 'message': f"{e.error_dict.get('message')}" })
    except Exception as e:
        print(f"{'[ CONTRO ERROR ]':<25} Error: {e}")
        return jsonify({ 'status': False, 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

    return jsonify({ 'status': True, 'data': best_schedule })

@generateJadwal.route("/generate_jadwal/upload_jadwal", methods=['POST'])
@login_required
def upload_jadwal():
    print(f"{'[ CONTROLLER ]':<25} Upload Jadwal")
    if session['user']['role'] == "ADMIN":
        req = request.get_json('data')
        data = dao.upload_jadwal(req['jadwal'])

    return jsonify( data )

@generateJadwal.route("/generate_jadwal/get_simpanan_prodi", methods=["GET"])
@login_required
def get_simpanan_prodi():
    print(f"{'[ CONTROLLER ]':<25} Get Simpanan Prodi")

    if session['user']['role'] == "ADMIN":
        data = dao.get_simpanan_prodi(session['user']['list_prodi'])

    return jsonify({ 'data': data })