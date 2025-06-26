from flask import Flask, redirect, url_for
from flask import request, session, jsonify
from flask_login import LoginManager
from datetime import datetime, timedelta, timezone
import os

from course_app.userModel import User
from course_app.dao.loginDao import loginDao

from course_app.controller.loginController import signin, session_generator
from course_app.controller.dashboardController import dashboard
from course_app.controller.settingController import setting
from course_app.controller.excelController import export

# ADMIN
from course_app.controller.admin.dataProgramStudiController import program_studi
from course_app.controller.admin.generateJadwalController import generateJadwal

# LABORAN
from course_app.controller.laboran.dataRuanganController import dataRuangan

# KAPRODI
from course_app.controller.kaprodi.dataDosenController import dosen
from course_app.controller.kaprodi.dataMataKuliahController import mataKuliah
from course_app.controller.kaprodi.mataKuliahPilihanController import mataKuliahPilihan

login_manager = LoginManager()

# Factory function untuk membuat aplikasi Flask
def create_app():
    print("[Vercel] create_app() called")
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    static_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')

    app = Flask(__name__,
            static_folder=static_dir,
            template_folder=template_dir)
    app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes=60)  # SESSION LIFETIME per 1 jam

    login_manager.init_app(app)
    login_manager.login_view = 'signin.login'

    @login_manager.user_loader
    def load_user(username):
        user_data = loginDao().get_user(username)
        if user_data:
            return User(username, user_data['data'])
        return None
    
    # Daftarkan Blueprint
    app.register_blueprint(signin)
    app.register_blueprint(dashboard)
    app.register_blueprint(setting)
    app.register_blueprint(export)

    # ADMIN
    app.register_blueprint(program_studi)
    app.register_blueprint(generateJadwal)

    # LABORAN
    app.register_blueprint(dataRuangan)

    # KAPRODI
    app.register_blueprint(dosen)
    app.register_blueprint(mataKuliah)
    app.register_blueprint(mataKuliahPilihan)
    
    # # Tambahkan konfigurasi tambahan jika diperlukan
    # app.config['SAMPLE_CONFIG'] = 'Sample Value'

    @app.errorhandler(401)
    def unathorized(e):
        return redirect(url_for('signin.login'))

    @app.errorhandler(404)
    def page_not_found(e):
        return redirect(url_for('signin.error404'))
    
    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    @app.route("/ping")
    def ping():
        print(f"{'❤ HEARTBEAT ❤':<25} Session: {True if session.get('user') else False}")
        is_alive = session.get('user') and 'u_id' in session['user']
        if not is_alive:
            return jsonify({'status': False, 'expired': True}), 401
        return jsonify({'status': True, 'expired': False}), 200

    @app.before_request
    def check_session():
        safe_endpoints = ['signin.login', 'signin.logout', 'static', 'signin.ping']
        current_endpoint = request.endpoint

        # SESSION

        # LIFETIME
        if current_endpoint is None or current_endpoint in safe_endpoints or "index" in current_endpoint:
            return
        
        print(f"{'[ 🔍 Before request ]':<25} Current Endpoint: {current_endpoint}")

        # Cek apakah session masih ada
        if not session.get('user') or 'u_id' not in session['user']:
            print(f"{'':<25} ⚠️ Session kosong atau tidak valid")
            return redirect(url_for('signin.logout'))

        # Jangan reset lifetime kalau hanya /ping
        if not request.path.startswith('/ping'):
            print(f"{'':<25} 🔄 Perpanjang lifetime session")
            session.permanent = True
            session.modified = True

        session_generator()

    # Cache control
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    return app
