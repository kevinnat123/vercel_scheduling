from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.laboran.dataRuanganDao import dataRuanganDao
from flask_login import login_required

dataRuangan = Blueprint('dataRuangan', __name__)
dao = dataRuanganDao()

@dataRuangan.route("/data_ruangan")
@login_required
def dataRuangan_index():
    print(f"{'[ RENDER ]':<15} Ruang Kelas (Role: {session['user']['role']})")
    if session['user']['role'] != 'LABORAN':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
            '/laboran/data_ruangan/index.html', 
            menu = 'Ruang Kelas', 
            title = 'Ruang Kelas', 
        )
    
@dataRuangan.route("/data_ruangan/post_kelas", methods=['POST'])
@login_required
def dataRuangan_post_kelas():
    print(f"{'[ CONTROLLER ]':<15} Post Kelas")
    req = request.get_json('data')
    data = dao.post_kelas(req)
    return jsonify( data )