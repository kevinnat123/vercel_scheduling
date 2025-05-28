from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.loginDao import loginDao
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from userModel import User
from datetime import datetime

signin = Blueprint('signin', __name__)
loginDao = loginDao()

@signin.before_request
def check_session():
    safe_endpoints = ['signin.login', 'signin.logout', 'static', 'signin.ping']
    current_endpoint = request.endpoint

    print(f"{'[ 🔍 Before request ]':<15} Current Endpoint: {current_endpoint}")

    if current_endpoint not in safe_endpoints:
        # Cek apakah session masih ada
        if not session.get('user') or 'u_id' not in session['user']:
            print(f"{'':<15} ⚠️ Session kosong atau tidak valid")
            return redirect(url_for('signin.logout'))

        # Jangan reset lifetime kalau hanya /ping
        if not request.path.startswith('/ping'):
            print(f"{'':<15} 🔄 Perpanjang lifetime session")
            session.permanent = True
            session.modified = True

        # Opsional: validasi extra user (misal di dashboard)
        if current_endpoint in ['signin.dashboard']:
            user_id_in_session = session['user'].get('u_id')
            user_id_in_db = loginDao.get_user_id(user_id_in_session)

            if not user_id_in_db or user_id_in_db != user_id_in_session:
                print(f"{'':<15} 🚫 User tidak valid di database")
                session.clear()
                return redirect(url_for('signin.logout'))

@signin.route("/ping")
def ping():
    print(f"{'❤ HEARTBEAT ❤':<15} Session: {True if session.get('user') else False}")
    if not session.get('user'):
        return jsonify({'status': False, 'expired': True}), 401
    return jsonify({'status': True, 'expired': False}), 200
            
@signin.route("/")
def home():
    print(f"{'[ THROW ]':<15} Login Page / Dashboard")
    if session.get('user') and 'u_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    return redirect(url_for('signin.login'))
    
@signin.route("/login", methods=['GET', 'POST'])
def login():
    print(f"{'[ CONTROLLER ]':<15} Login (Method: {request.method})")
    if session.get('user') and 'u_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    
    if request.method == 'POST':
        req = request.get_json('data')
        nip = req.get('nip')
        password = req.get('password')

        # user = loginDao.signUp(nip, password)
        user = loginDao.verify_user(nip, password)

        if user['status']:
            user_obj = User(nip, user['data'])
            login_user(user_obj)

            menu = loginDao.get_menu(session['user']['role'])
            session['menu'] = menu if menu else []
            session['academic_details'] = get_academic_details()

            session.permanent = True  # Aktifkan waktu hidup session

            print(f"{'':<15} {'Session Academic_Details':<30}: {session['academic_details']}")
            print(f"{'':<15} {'Session User':<30}: {session['user']}")
            print(f"{'':<15} {'Session Menu':<30}: {session['menu']}")
            return jsonify({'status': True, 'redirect_url': url_for('dashboard.dashboard_index')}), 200
            # return jsonify({'status': True, 'redirect_url': url_for('signin.dashboard')}), 200

        return jsonify({'status': False, 'message': user['message']}), 401
    return render_template('signin.html')

@signin.route("/dashboard")
@login_required
def dashboard():
    print(f"{'[ RENDER ]':<15} Dashboard")

    # Pastikan session masih valid
    if not session.get('user') or 'u_id' not in session['user']:
        print("⚠️ Session tidak valid, redirect ke login")
        return redirect(url_for('signin.login'))
    
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

def get_academic_details():
    today = datetime.today()
    current_year = today.year
    max_year = current_year if today.month >= 7 else current_year - 1
    min_year = max_year - 7

    # Menentukan semester saat ini
    if today.month <= 3:
        semester_saat_ini = "Antara"
        semester_depan = "Genap"
    elif today.month <= 8:
        semester_saat_ini = "Genap"
        semester_depan = "Gasal"
    else:
        semester_saat_ini = "Gasal"
        semester_depan = "Antara"

    # Menentukan tahun ajaran
    tahun_ajaran_1 = (current_year - 1) if today.month <= 8 else current_year
    tahun_ajaran = f"{current_year - 1}/{current_year}" if today.month <= 8 else f"{current_year}/{current_year + 1}"

    list_angkatan = list(range(min_year, max_year + 1))

    return {
        "min_year": min_year,
        "max_year": max_year,
        "semester_saat_ini": semester_saat_ini,
        "semester_depan": semester_depan,
        "tahun_ajaran_1": tahun_ajaran_1,
        "tahun_ajaran": tahun_ajaran,
        "list_angkatan": list_angkatan
    }

@signin.route("/404NotFound")
@login_required
def error404():
    print(f"{'[ RENDER ]':<15} Error 404")
    if not session.get('user') or 'u_id' not in session['user']:
        return redirect(url_for('signin.login'))

    return render_template('404.html', menu = "404 Not Found", redirect_url = url_for('signin.dashboard'))

@signin.route("/403Forbidden")
@login_required
def error403():
    print(f"{'[ RENDER ]':<15} Error 403")
    if not session.get('user') or 'u_id' not in session['user']:
        return redirect(url_for('signin.login'))

    return render_template('403.html', menu = "403 Forbidden", redirect_url = url_for('signin.dashboard'))

@signin.route("/logout")
def logout():
    print(f"{'[ THROW ]':<15} Logout")
    logout_user()
    session.clear()  # Pastikan semua session terhapus
    return redirect(url_for('signin.login'))