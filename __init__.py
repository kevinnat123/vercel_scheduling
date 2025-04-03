from flask import Flask, redirect, url_for
from flask_login import LoginManager
from userModel import User
from dao.loginDao import loginDao

from controller.loginController import signin

# ADMIN
from controller.admin.generateJadwalController import generateJadwal

# LABORAN
from controller.laboran.ruangKelasController import ruangKelas

# KAPRODI
from controller.kaprodi.dataDosenController import dosen
from controller.kaprodi.dataMataKuliahController import mataKuliah
from controller.kaprodi.mataKuliahPilihanController import mataKuliahPilihan

login_manager = LoginManager()

# Factory function untuk membuat aplikasi Flask
def create_app():
    app = Flask(__name__)

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

    # ADMIN
    app.register_blueprint(generateJadwal)

    # LABORAN
    app.register_blueprint(ruangKelas)

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

    # Cache control
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    return app
