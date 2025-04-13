from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.laboran.ruangKelasDao import ruangKelasDao
from flask_login import login_required

ruangKelas = Blueprint('ruangKelas', __name__)
dao = ruangKelasDao()

@ruangKelas.route("/ruang_kelas")
@login_required
def ruangKelas_index():
    print('========== ========== ========== ========== RENDER RUANG KELAS  ========== ========== ========== ==========')
    if session['user']['role'] != 'LABORAN':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
            '/laboran/ruang_kelas/index.html', 
            menu = 'Ruang Kelas', 
            title = 'Ruang Kelas', 
        )
    
@ruangKelas.route("/ruang_kelas/post_kelas", methods=['POST'])
@login_required
def mataKuliah_post_kelas():
    print('[ CONTROLLER ] post_kelas')
    req = request.get_json('data')
    data = dao.post_kelas(req)
    return jsonify( data )