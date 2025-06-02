from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.admin.generateJadwalDao import generateJadwalDao
from flask_login import login_required

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def generateJadwal_index():
    print(f"{'[ RENDER ]':<15} Generate Jadwal (Role: {session['user']['role']})")
    if session['user']['role'] != 'ADMIN':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
            '/admin/generate_jadwal/index.html', 
            menu = 'Generate Jadwal', 
            title = 'Generate Jadwal', 
        )
    
@generateJadwal.route("/generate_jadwal/generate", methods=['GET'])
@login_required
def generate_jadwal():
    print(f"{'[ CONTROLLER ]':<15} Generate Jadwal")

    try:
        data_dosen = dao.get_dosen()
        data_matkul = dao.get_matkul()
        data_ruang = dao.get_kelas()

        best_schedule = ga.genetic_algorithm(
            data_matkul, data_dosen, data_ruang, 
            ukuran_populasi=75, jumlah_generasi=1, peluang_mutasi=0.05
        )

        dao.upload_jadwal(best_schedule)
    except Exception as e:
        print(f"{'[ CONTRO ERROR ]':<15} Error: {e}")
        return jsonify({ 'status': False, 'message': 'Terjadi kesalahan sistem. Harap hubungi Admin.' })

    return jsonify({ 'status': True, 'data': best_schedule })

@generateJadwal.route("/generate_jadwal/upload_jadwal", methods=['POST'])
@login_required
def upload_jadwal():
    print(f"{'[ CONTROLLER ]':<15} Upload Jadwal")
    if session['user']['role'] == "ADMIN":
        req = request.get_json('data')
        data = dao.upload_jadwal(req['jadwal'])

    return jsonify( data )