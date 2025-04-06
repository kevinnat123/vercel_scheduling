from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.settingDao import settingDao
from flask_login import login_user, logout_user, login_required

setting = Blueprint('setting', __name__)
settingDao = settingDao()

@setting.route("/setting")
@login_required
def setting_index():
    print('========== ========== ========== ========== RENDER SETTING KAPRODI  ========== ========== ========== ==========')
    return render_template(
            '/setting.html', 
            menu = 'Setting', 
            title = 'Setting', 
        )
    
@setting.route("/password_verification", methods=['GET', 'POST'])
@login_required
def setting_passwordVerification():
    print('[ CONTROLLER ] password_verification', request.method, session.get('user'))
    if request.method == 'POST':
        req = request.get_json('data')
        oldPassword = req.get('oldPassword')
        newPassword = req.get('newPassword')
        verifyNewPassword = req.get('verifyNewPassword')

        manage_new_password = settingDao.register_new_password(oldPassword, newPassword, verifyNewPassword)
        # manage_new_password.update({ 'redirect_url': url_for('signin.logout') }) # REMINDER: BEBAS PAKAI
            
    return jsonify( manage_new_password )