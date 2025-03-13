from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from pymongo import MongoClient
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()
mongo = None

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    CORS(app)
    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    # Initialize MongoDB
    global mongo
    mongo = MongoClient(app.config['MONGODB_URI'])

    # Register blueprints
    from app.api.auth import bp as auth_bp
    app.register_blueprint(auth_bp, url_prefix='/api/auth')

    from app.api.users import bp as users_bp
    app.register_blueprint(users_bp, url_prefix='/api/users')

    from app.api.health_records import bp as health_records_bp
    app.register_blueprint(health_records_bp, url_prefix='/api/health-records')

    from app.api.assessments import bp as assessments_bp
    app.register_blueprint(assessments_bp, url_prefix='/api/assessments')

    @app.route('/health')
    def health_check():
        return {'status': 'healthy'}

    return app 