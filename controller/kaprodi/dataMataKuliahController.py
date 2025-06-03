from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.kaprodi.dataMataKuliahDao import dataMataKuliahDao
from flask_login import login_required

mataKuliah = Blueprint('mataKuliah', __name__)
dao = dataMataKuliahDao()

@mataKuliah.route("/data_mata_kuliah")
@login_required
def mataKuliah_index():
    print(f"{'[ RENDER ]':<15} Data Mata Kuliah (Role: {session['user']['role']})")
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
def mataKuliah_tambah_kelompok():
    print(f"{'[ CONTROLLER ]':<15} Post Kelompok Matakuliah")
    data = request.get_json('data')
    nama_baru = data.get("nama")
    
    if nama_baru:
        data = dao.put_kelompok(nama_baru)
        return jsonify(data)

    return jsonify({"status": False}), 400

@mataKuliah.route("/data_mata_kuliah/get_matkul", methods=['GET'])
@login_required
def mataKuliah_get_matkul():
    print(f"{'[ CONTROLLER ]':<15} Get Matkul")
    data = dao.get_matkul()
    for matkul in data:
        if not matkul.get('asistensi'):
            matkul['asistensi'] = False
    return jsonify({ 'data': data })

@mataKuliah.route("/data_mata_kuliah/post_matkul", methods=['POST'])
@login_required
def mataKuliah_post_matkul():
    print(f"{'[ CONTROLLER ]':<15} Post Matkul")
    req = request.get_json('data')
    data = dao.post_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/put_matkul", methods=['POST'])
@login_required
def mataKuliah_put_matkul():
    print(f"{'[ CONTROLLER ]':<15} Put Matkul")
    req = request.get_json('data')
    data = dao.put_matkul(req)
    return jsonify( data )

@mataKuliah.route("/data_mata_kuliah/delete_matkul", methods=['POST'])
@login_required
def mataKuliah_delete_matkul():
    print(f"{'[ CONTROLLER ]':<15} Delete Matkul")
    req = request.get_json('data')
    data = dao.delete_matkul(req)
    return jsonify( data )