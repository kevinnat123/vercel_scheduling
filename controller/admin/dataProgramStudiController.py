from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from flask.wrappers import Response
from dao.admin.dataProgramStudiDao import dataProgramStudiDao
from dao.kaprodi.dataDosenDao import dataDosenDao
from flask_login import login_required

program_studi = Blueprint('program_studi', __name__)
dao = dataProgramStudiDao()
dao_dosen = dataDosenDao()

@program_studi.route("/data_program_studi")
@login_required
def program_studi_index():
    print(f"{'[ RENDER ]':<15} Data Program Studi (Role: {session['user']['role']})")
    print('========== ========== ========== ========== RENDER DATA PROGRAM STUDI  ========== ========== ========== ==========')
    if session['user']['role'] not in ["ADMIN"]:
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
                '/admin/data_program_studi/index.html', 
                menu = 'Data Program Studi', 
                title = 'Data Program Studi', 
            )
    
@program_studi.route("/data_program_studi/get_program_studi", methods=['GET'])
@login_required
def program_studi_get_program_studi() -> Response:
    print(f"{'[ CONTROLLER ]':<15} Get Program Studi")
    data = dao.get_prodi()
    for prodi in data:
        prodi['status_aktif'] = "AKTIF" if prodi["status_aktif"] else "NONAKTIF"
        if prodi.get("kepala_program_studi"):
            prodi["kepala_program_studi"] = dao_dosen.get_dosen_by_nip(prodi["kepala_program_studi"]).get("nama", prodi.get('kepala_program_studi', None))
    return jsonify({ 'data': data })

@program_studi.route("/data_program_studi/post_program_studi", methods=['POST'])
@login_required
def program_studi_post_program_studi() -> Response:
    print(f"{'[ CONTROLLER ]':<15} Post Program Studi")
    req = request.get_json('data')
    data = dao.post_prodi(req)
    return jsonify( data )