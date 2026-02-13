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
    login_manager.login_view = 'auth.login'
    oauth.init_app(app)
    
    # Register USP OAuth
    if app.config.get('USP_CLIENT_KEY') and app.config.get('USP_CLIENT_SECRET'):
        oauth.register(
            name='usp',
            client_id=app.config['USP_CLIENT_KEY'],
            client_secret=app.config['USP_CLIENT_SECRET'],
            request_token_url='https://uspdigital.usp.br/wsusuario/oauth/request_token',
            access_token_url='https://uspdigital.usp.br/wsusuario/oauth/access_token',
            authorize_url='https://uspdigital.usp.br/wsusuario/oauth/authorize',
            api_base_url='https://uspdigital.usp.br/wsusuario/oauth/'
        )

    # Register Blueprints
    from blueprints.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    from blueprints.main import main_bp
    app.register_blueprint(main_bp)

    from blueprints.admin import admin_bp
    app.register_blueprint(admin_bp)

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(port=5001)
