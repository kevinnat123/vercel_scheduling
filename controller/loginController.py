from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.loginDao import loginDao
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from userModel import User

signin = Blueprint('signin', __name__)
loginDao = loginDao()

@signin.before_request
def check_session():
    """ Periksa apakah session user masih valid, jika tidak logout otomatis """
    if request.endpoint not in ['signin.login', 'signin.logout']:  # Hindari loop logout
        if not session.get('user') or 'u_id' not in session['user']:
            # Tambahkan counter untuk mendeteksi redirect loop
            session['redirect_count'] = session.get('redirect_count', 0) + 1
            if session['redirect_count'] > 3:  # Misal redirect lebih dari 3 kali
                print("⚠️ Terlalu banyak redirect! Logout otomatis...")
                session.clear()
                return redirect(url_for('signin.login'))
            return redirect(url_for('signin.logout'))
        
        # 🛑 **Tambahan: Cek apakah session yang ada berbeda dengan data user yang diharapkan**
        if request.endpoint in ['signin.dashboard']:  # Pastikan hanya mengecek di halaman tertentu
            user_id_in_session = session['user'].get('u_id')
            user_id_in_db = loginDao.get_user_id(user_id_in_session)  # Fungsi ambil user dari DB
            print('user_id_in_session', user_id_in_session, 'user_id_in_db', user_id_in_db)

            if not user_id_in_db or user_id_in_db != user_id_in_session:
                print("⚠️ Session tidak valid! Logout otomatis...")
                session.clear()
                return redirect(url_for('signin.logout'))
    session.pop('redirect_count', None)  # Reset counter jika sukses login

@signin.route("/")
def home():
    print('[ CONTROLLER ] render website')
    if session.get('user') and 'u_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    return redirect(url_for('signin.login'))
    
@signin.route("/login", methods=['GET', 'POST'])
def login():
    print('[ CONTROLLER ] login', request.method, session.get('user'))
    if session.get('user') and 'u_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    
    if request.method == 'POST':
        req = request.get_json('data')
        nip = req.get('nip')
        password = req.get('password')
        print('  nip', nip)
        print('  password', password)

        # user = loginDao.signUp(nip, password)
        user = loginDao.verify_user(nip, password)
        print('  user', user)

        if user['status']:
            user_obj = User(nip, user['data'])
            login_user(user_obj)

            menu = loginDao.get_menu(session['user']['role'])
            session['menu'] = menu if menu else []

            print('  session        :', session)
            print('  session user   :', session['user'])
            print('  session menu   :', session['menu'])
            return jsonify({'status': True, 'redirect_url': url_for('signin.dashboard')}), 200

        return jsonify({'status': False, 'message': user['message']}), 401
    return render_template('signin.html')

@signin.route("/dashboard")
@login_required
def dashboard():
    print('[ CONTROLLER ] dashboard')

    # Pastikan session masih valid
    if not session.get('user') or 'u_id' not in session['user']:
        print("⚠️ Session tidak valid, redirect ke login")
        return redirect(url_for('signin.login'))

    return render_template('index.html', menu='Dashboard', title='Dashboard')

@signin.route("/404")
@login_required
def error404():
    print('[ CONTROLLER ] error404')
    if not session.get('user') or 'u_id' not in session['user']:
        return redirect(url_for('signin.login'))

    return render_template('404.html')

@signin.route("/403")
def error403():
    print('[ CONTROLLER ] error403')
    if not session.get('user') or 'u_id' not in session['user']:
        return redirect(url_for('signin.login'))

    return render_template('403.html')

@signin.route("/logout")
def logout():
    print('[ CONTROLLER ] logout')
    logout_user()
    session.clear()  # Pastikan semua session terhapus
    return redirect(url_for('signin.login'))
