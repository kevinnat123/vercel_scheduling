from flask import Flask

from controller.loginController import main_routes

# Factory function untuk membuat aplikasi Flask
def create_app():
    app = Flask(__name__)
    
    # Daftarkan Blueprint
    app.register_blueprint(main_routes)
    
    # Tambahkan konfigurasi tambahan jika diperlukan
    app.config['SAMPLE_CONFIG'] = 'Sample Value'

    # Cache control
    @app.after_request
    def add_cache_control(response):
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"
        return response
    
    return app
