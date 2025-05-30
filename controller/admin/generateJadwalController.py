from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.admin.generateJadwalDao import generateJadwalDao
from dao import genetic_algorithm as ga
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
    data_dosen = dao.get_dosen()
    data_matkul = dao.get_matkul()
    data_ruang = dao.get_kelas()

    best_schedule = ga.genetic_algorithm(
        data_matkul, data_dosen, data_ruang, 
        ukuran_populasi=75, jumlah_generasi=100, peluang_mutasi=0.05
    )

    ga.export_jadwal_to_excel(best_schedule, "jadwal_kuliah.xlsx", data_matkul, data_dosen)
    
    return jsonify({ 'data': best_schedule })