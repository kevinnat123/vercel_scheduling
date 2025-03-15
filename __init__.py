from flask import Flask

from controller.first import main_routes

# Factory function untuk membuat aplikasi Flask
def create_app():
    app = Flask(__name__)
    
    # Daftarkan Blueprint
    app.register_blueprint(main_routes)
    
    # Tambahkan konfigurasi tambahan jika diperlukan
    app.config['SAMPLE_CONFIG'] = 'Sample Value'
    
    return app
