from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from dao.loginDao import loginDao
from flask_login import login_user, logout_user, login_required
from werkzeug.security import check_password_hash
from userModel import User

signin = Blueprint('signin', __name__)
loginDao = loginDao()

@signin.route("/")
def home():
    print('[ CONTROLLER ] render website')
    if session.get('user') and '_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    return redirect(url_for('signin.login'))
    
@signin.route("/login", methods=['GET', 'POST'])
def login():
    print('[ CONTROLLER ] login', request.method, session.get('user'))
    if session.get('user') and '_id' in session['user']:
        return redirect(url_for('signin.dashboard'))
    
    if request.method == 'POST':
        req = request.get_json('data')
        username = req.get('username')
        password = req.get('password')
        print('  username', username)
        print('  password', password)

        # user = loginDao.signUp(username, password)
        user = loginDao.verify_user(username, password)
        print('  user', user)

        if user['status']:
            user_obj = User(username, user['data'])
            login_user(user_obj)
            print('  session        :', session)
            print('  session user   :', session['user'])
            print('  session menu   :', session['menu'])
            # return redirect(url_for('signin.dashboard'))
            return jsonify({'status': True, 'redirect_url': url_for('signin.dashboard')}), 200

        return jsonify({'status': False, 'message': user['message']}), 401
    return render_template('signin.html')

@signin.route("/dashboard")
@login_required
def dashboard():
    print('[ CONTROLLER ] dashboard')
    if not session.get('user') or '_id' not in session['user']:
        return redirect(url_for('signin.login'))
    
    menu = loginDao.get_menu(session['user']['role'])
    session['menu'] = menu if menu else []
    return render_template(
        'index.html', 
        menu = 'Dashboard', 
        title = 'Dashboard'
    )

@signin.route("/logout")
# @login_required
def logout():
    print('[ CONTROLLER ] logout')
    logout_user()
    session.pop('user', None)  # Hapus session dengan aman
    return redirect(url_for('signin.login'))