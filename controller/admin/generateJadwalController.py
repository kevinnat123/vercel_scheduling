from flask import render_template, Blueprint, request, jsonify, session, redirect, url_for
from dao.admin.generateJadwalDao import generateJadwalDao
from flask_login import login_required

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def generateJadwal_index():
    print('[ CONTROLLER ] render generate jadwal')
    if session['user']['role'] != 'ADMIN':
        return redirect(url_for('signin.error403'))
    else:
        return render_template(
            '/admin/generate_jadwal/index.html', 
            menu = 'Generate Jadwal', 
            title = 'Generate Jadwal', 
        )