from flask import Flask
from flask_login import LoginManager
from controller.loginController import main_routes
from dao.loginDao import loginDao
from userModel import User

login_manager = LoginManager()

# Factory function untuk membuat aplikasi Flask
def create_app():
    app = Flask(__name__)

    login_manager.init_app(app)
    login_manager.login_view = 'main_routes.login'

    @login_manager.user_loader
    def load_user(username):
        user_data = loginDao().get_user(username)
        if user_data:
            return User(username, user_data['data'])
        return None
    
    # Daftarkan Blueprint
    app.register_blueprint(main_routes)
    
    # # Tambahkan konfigurasi tambahan jika diperlukan
    # app.config['SAMPLE_CONFIG'] = 'Sample Value'

    # Cache control
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    return app
