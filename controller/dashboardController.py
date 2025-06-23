from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.dashboardDao import dashboardDao
from flask_login import login_user, logout_user, login_required

dashboard = Blueprint('dashboard', __name__)
dashboardDao = dashboardDao()

@dashboard.route("/dashboard")
@login_required
def dashboard_index():
    print(f"{'[ RENDER ]':<25} Dashboard (Role: {session['user']['role']})")
    if session['user']['role'] == 'KEPALA PROGRAM STUDI':
        return render_template(
                '/kaprodi/dashboard.html', 
                menu = 'Dashboard', 
                title = 'Dashboard', 
                prodi = session['user']['prodi'],
                kelompok_matkul = session['user']['kelompok_matkul'],
                bidang_minat = session['user']['bidang_minat']
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
                list_prodi = session['user']['list_prodi']
            )
    else:
        return redirect(url_for('signin.error403'))

@dashboard.route("/update_general", methods=['POST'])
@login_required
def dashboardKaprodi_updateGeneral():
    print(f"{'[ CONTROLLER ]':<25} Update General")
    req = request.get_json('data')

    result = dashboardDao.update_general(req)

    if (result.get('status') == False and result.get('message') == 'User Not Found'):
        return redirect(url_for('signin.logout'))
            
    return jsonify( result )

@dashboard.route("/update_kelompok_matkul", methods=['POST'])
@login_required
def dashboardKaprodi_updateKelompokMatkul():
    print(f"{'[ CONTROLLER ]':<25} Update Kelompok Matkul")
    
    req = request.get_json('data')

    result = dashboardDao.update_kelompokMatkul(req)

    return jsonify( result )

@dashboard.route("/update_bidang_minat", methods=['POST'])
@login_required
def dashboardKaprodi_updateBidangMinat():
    print(f"{'[ CONTROLLER ]':<25} Update Bidang Minat")
    
    req = request.get_json('data')

    result = dashboardDao.update_bidangMinat(req)

    return jsonify( result )

@dashboard.route("/update_os", methods=['POST'])
@login_required
def dashboardLaboran_updateOs():
    print(f"{'[ CONTROLLER ]':<25} Update OS")
    
    req = request.get_json('data')

    result = dashboardDao.update_os(req)

    return jsonify( result )

@dashboard.route("/update_processor", methods=['POST'])
@login_required
def dashboardLaboran_updateProcessor():
    print(f"{'[ CONTROLLER ]':<25} Update Processor")
    
    req = request.get_json('data')

    result = dashboardDao.update_processor(req)

    return jsonify( result )

@dashboard.route("/update_prodi", methods=['POST'])
@login_required
def dashboardLaboran_updateProdi():
    print(f"{'[ CONTROLLER ]':<25} Update Prodi")
    
    req = request.get_json('data')

    result = dashboardDao.update_prodi(req)

    return jsonify( result )