from flask import Flask
from config import Config
from extensions import db, migrate, login_manager, oauth

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Init Extensions
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    oauth.init_app(app)

    # Register Blueprints (to be created)
    # from blueprints.main import main_bp
    # app.register_blueprint(main_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5001)
