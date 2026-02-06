from flask import Flask
from app.extensions import db, login_manager, mail
import os


def create_app():
    app = Flask(
        __name__,
        static_folder="static",        # 👈 IMPORTANTE
        static_url_path="/static"      # 👈 IMPORTANTE
    )
    
    app.config["SECRET_KEY"] = "cisaa-secret-key"
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///cisaa.db"
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    # ===== CONFIG EMAIL =====
    app.config["MAIL_SERVER"] = "smtp.gmail.com"      # AJUSTAR
    app.config["MAIL_PORT"] = 587                      # o 465
    app.config["MAIL_USE_TLS"] = True
    app.config["MAIL_USE_SSL"] = False
    app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
    app.config["MAIL_DEFAULT_SENDER"] = "laboratoriocisaa@gmail.com>"

    db.init_app(app)
    login_manager.init_app(app)
    mail.init_app(app)


    from app.routes.main import main_bp
    from app.routes.admin import admin_bp
    from app.routes.service import services_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(admin_bp)
    app.register_blueprint(services_bp)

    return app
