from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.kaprodi.mataKuliahPilihanDao import mataKuliahPilihanDao
from flask_login import login_required

mataKuliahPilihan = Blueprint('mataKuliahPilihan', __name__)
dao = mataKuliahPilihanDao()

@mataKuliahPilihan.route("/mata_kuliah_pilihan")
@login_required
def mataKuliah_index():
    print('========== ========== ========== ========== RENDER MATA KULIAH PILIHAN  ========== ========== ========== ==========')
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
def get_lovMatkul():
    print('[ CONTROLLER ] get_lovMatkul')
    data = dao.get_lovMatkul()
    return jsonify({ 'data': data })

@mataKuliahPilihan.route("/mata_kuliah_pilihan/post_matkul", methods=['POST'])
@login_required
def post_matkul():
    print('[ CONTROLLER ] post_matkul')
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/put_matkul", methods=['POST'])
@login_required
def put_matkul():
    print('[ CONTROLLER ] put_matkul')
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliahPilihan.route("/mata_kuliah_pilihan/delete_data", methods=['POST'])
@login_required
def delete_data():
    print('[ CONTROLLER ] delete_data')
    req = request.get_json('data')
    data = dao.delete_data(req)
    return jsonify( data )