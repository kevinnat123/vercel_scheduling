from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.dashboardDao import dashboardDao
from flask_login import login_user, logout_user, login_required

dashboard = Blueprint('dashboard', __name__)
dashboardDao = dashboardDao()

@dashboard.route("/dashboard")
@login_required
def dashboard_index():
    print('========== ========== ========== ========== RENDER DASHBOARD  ========== ========== ========== ==========')
    if session['user']['role'] == 'KEPALA PROGRAM STUDI':
        return render_template(
                '/kaprodi/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
                prodi = session['user']['prodi'],
                kelompok_matkul = session['user']['kelompok_matkul']
            )
    elif session['user']['role'] == 'LABORAN':
        return render_template(
                '/laboran/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
                list_os = session['user']['list_os'],
                list_processor = session['user']['list_processor']
            )
    elif session['user']['role'] == 'ADMIN':
        return render_template(
                '/admin/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
            )
    else:
        return redirect(url_for('signin.error403'))

@dashboard.route("/update_general", methods=['POST'])
@login_required
def dashboardKaprodi_updateGeneral():
    print('[ CONTROLLER ] update_general', request.method, session.get('user'))
    req = request.get_json('data')

    result = dashboardDao.update_general(req)

    if (result.get('status') == False and result.get('message') == 'User Not Found'):
        return redirect(url_for('signin.logout'))
            
    return jsonify( result )

@dashboard.route("/update_kelompok_matkul", methods=['POST'])
@login_required
def dashboardKaprodi_updateKelompokMatkul():
    print('[ CONTROLLER ] update_kelompokMatkul')
    
    req = request.get_json('data')

    result = dashboardDao.update_kelompokMatkul(req)

    return jsonify( result )

@dashboard.route("/update_os", methods=['POST'])
@login_required
def dashboardLaboran_updateOs():
    print('[ CONTROLLER ] update_os')
    
    req = request.get_json('data')

    result = dashboardDao.update_os(req)

    return jsonify( result )

@dashboard.route("/update_processor", methods=['POST'])
@login_required
def dashboardLaboran_updateProcessor():
    print('[ CONTROLLER ] update_processor')
    
    req = request.get_json('data')

    result = dashboardDao.update_processor(req)

    return jsonify( result )