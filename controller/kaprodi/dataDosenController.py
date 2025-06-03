from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.kaprodi.dataDosenDao import dataDosenDao
from flask_login import login_required

dosen = Blueprint('dosen', __name__)
dao = dataDosenDao()

@dosen.route("/data_dosen")
@login_required
def dosen_index():
    print(f"{'[ RENDER ]':<15} Data Dosen (Role: {session['user']['role']})")
    print('========== ========== ========== ========== RENDER DATA DOSEN  ========== ========== ========== ==========')
    if session['user']['role'] != 'KEPALA PROGRAM STUDI':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
                '/kaprodi/data_dosen/index.html', 
                menu = 'Data Dosen', 
                title = 'Data Dosen', 
                prodi = session['user']['prodi']
            )
    
@dosen.route("/data_dosen/get_dosen", methods=['GET'])
@login_required
def get_dosen():
    print(f"{'[ CONTROLLER ]':<15} Get Dosen")
    data = dao.get_dosen()
    return jsonify({ 'data': data })

@dosen.route("/data_dosen/post_dosen", methods=['POST'])
@login_required
def post_dosen():
    print(f"{'[ CONTROLLER ]':<15} Post Dosen")
    req = request.get_json('data')
    data = dao.post_dosen(req)
    return jsonify( data )

@dosen.route("/data_dosen/put_dosen", methods=['POST'])
@login_required
def put_dosen():
    print(f"{'[ CONTROLLER ]':<15} Put Dosen")
    req = request.get_json('data')
    data = dao.put_dosen(req)
    return jsonify( data )

@dosen.route("/data_dosen/delete_dosen", methods=['POST'])
@login_required
def delete_dosen():
    print(f"{'[ CONTROLLER ]':<15} Delete Dosen")
    req = request.get_json('data')
    data = dao.delete_dosen(req)
    return jsonify( data )