from flask import render_template, Blueprint, request, jsonify, session
from dao.admin.generateJadwalDao import generateJadwalDao
from flask_login import login_required

generateJadwal = Blueprint('generateJadwal', __name__)
dao = generateJadwalDao()

@generateJadwal.route("/generate_jadwal")
@login_required
def home():
    print('[ CONTROLLER ] render generate jadwal')
    return render_template(
        '/admin/generate_jadwal/index.html', 
        menu = 'Generate Jadwal', 
        title = 'Generate Jadwal', 
    )