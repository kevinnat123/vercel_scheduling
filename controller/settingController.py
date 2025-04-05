from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.settingDao import settingDao
from flask_login import login_user, logout_user, login_required

setting = Blueprint('setting', __name__)
settingDao = settingDao()

@setting.route("/setting")
@login_required
def settingKaprodi_index():
    print('========== ========== ========== ========== RENDER SETTING KAPRODI  ========== ========== ========== ==========')
    if session['user']['role'] == 'KEPALA PROGRAM STUDI':
        return render_template(
                '/kaprodi/setting.html', 
                menu = 'Setting', 
                title = 'Setting', 
                prodi = session['user']['prodi'],
                kelompok_matkul = session['user']['kelompok_matkul']
            )
    else:
        return redirect(url_for('signin.error403'))
    
@setting.route("/password_verification", methods=['GET', 'POST'])
@login_required
def settingKaprodi_password_verification():
    print('[ CONTROLLER ] password_verification', request.method, session.get('user'))
    if request.method == 'POST':
        req = request.get_json('data')
        oldPassword = req.get('oldPassword')
        newPassword = req.get('newPassword')
        verifyNewPassword = req.get('verifyNewPassword')

        manage_new_password = settingDao.register_new_password(oldPassword, newPassword, verifyNewPassword)
        # manage_new_password.update({ 'redirect_url': url_for('signin.logout') }) # REMINDER: BEBAS PAKAI
            
    return jsonify( manage_new_password )

@setting.route("/update_general", methods=['POST'])
@login_required
def settingKaprodi_update_general():
    print('[ CONTROLLER ] update_general', request.method, session.get('user'))
    req = request.get_json('data')

    result = settingDao.update_general(req)

    if (result.get('status') == False and result.get('message') == 'User Not Found'):
        return redirect(url_for('signin.logout'))
            
    return jsonify( result )

@setting.route("/update_kelompok_matkul", methods=['POST'])
@login_required
def settingKaprodi_update_kelompokMatkul():
    print('[ CONTROLLER ] update_kelompokMatkul')
    
    req = request.get_json('data')

    result = settingDao.update_kelompokMatkul(req)

    return jsonify( result )