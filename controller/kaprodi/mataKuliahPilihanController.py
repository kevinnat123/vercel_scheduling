from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.kaprodi.mataKuliahPilihanDao import mataKuliahPilihanDao
from flask_login import login_required

mataKuliahPilihan = Blueprint('mataKuliahPilihan', __name__)
dao = mataKuliahPilihanDao()

@mataKuliahPilihan.route("/mata_kuliah_pilihan")
@login_required
def mataKuliahPilihan_index():
    print(f"{'[ RENDER ]':<15} Mata Kuliah Pilihan (Role: {session['user']['role']})")
    if session['user']['role'] != 'KEPALA PROGRAM STUDI':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
                '/kaprodi/mataKuliah_pilihan/index.html', 
                menu = 'Mata Kuliah Pilihan', 
                title = 'Mata Kuliah Pilihan', 
                prodi = session['user']['prodi'],
                maks_sks = int(session['user']['maks_sks_prodi']),
                data_sebelum = dao.get_listMatkulTersimpan() or []
            )
    
@mataKuliahPilihan.route("/mata_kuliah_pilihan/get_lovMatkul", methods=['GET'])
@login_required
def mataKuliahPilihan_get_lovMatkul():
    print(f"{'[ CONTROLLER ]':<15} Get LOV Matkul")
    data = dao.get_lovMatkul()
    return jsonify({ 'data': data })

@mataKuliahPilihan.route("/mata_kuliah_pilihan/post_matkul", methods=['POST'])
@login_required
def mataKuliahPilihan_post_matkul():
    print(f"{'[ CONTROLLER ]':<15} Post Matkul Pilihan")
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/put_matkul", methods=['POST'])
@login_required
def mataKuliahPilihan_put_matkul():
    print(f"{'[ CONTROLLER ]':<15} Put Matkul Pilihan")
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/delete_data", methods=['POST'])
@login_required
def mataKuliahPilihan_delete_data():
    print(f"{'[ CONTROLLER ]':<15} Delete Matkul Pilihan")
    req = request.get_json('data')
    data = dao.delete_data(req)
    return jsonify( data )