from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
from flask_login import login_required

mataKuliah = Blueprint('mataKuliah', __name__)
dao = dataMataKuliahDao()

@mataKuliah.route("/data_mata_kuliah")
@login_required
def mataKuliah_index():
    print('========== ========== ========== ========== RENDER DATA MATA KULIAH  ========== ========== ========== ==========')
    if session['user']['role'] != 'KEPALA PROGRAM STUDI':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
                '/kaprodi/data_mataKuliah/index.html', 
                menu = 'Data Mata Kuliah', 
                title = 'Data Mata Kuliah', 
                prodi = session['user']['prodi']
            )
    
@mataKuliah.route("/data_mata_kuliah/post_kelompok", methods=["POST"])
@login_required
def tambah_kelompok():
    data = request.get_json('data')
    nama_baru = data.get("nama")
    
    if nama_baru:
        data = dao.put_kelompok(nama_baru)
        return jsonify(data)

    return jsonify({"status": False}), 400

@mataKuliah.route("/data_mata_kuliah/get_matkul", methods=['GET'])
@login_required
def get_matkul():
    print('[ CONTROLLER ] get_matkul')
    data = dao.get_matkul()
    return jsonify({ 'data': data })

@mataKuliah.route("/data_mata_kuliah/post_matkul", methods=['POST'])
@login_required
def post_matkul():
    print('[ CONTROLLER ] post_matkul')
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/put_matkul", methods=['POST'])
@login_required
def put_matkul():
    print('[ CONTROLLER ] put_matkul')
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/delete_matkul", methods=['POST'])
@login_required
def delete_matkul():
    print('[ CONTROLLER ] delete_matkul')
    req = request.get_json('data')
    print('  req', req)
    data = dao.delete_matkul(req)
    return jsonify( data )