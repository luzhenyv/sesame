from flask import Flask
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from flask_jwt_extended import JWTManager
from flask_marshmallow import Marshmallow
from config import Config

db = SQLAlchemy()
ma = Marshmallow()
jwt = JWTManager()


def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Enable CORS for all routes
    CORS(app, supports_credentials=True)

    db.init_app(app)
    ma.init_app(app)
    jwt.init_app(app)

    # Register blueprints
    from app.api.hello import bp as hello_bp

    app.register_blueprint(hello_bp, url_prefix="/api")

    @app.route("/health")
    def health_check():
        return {"status": "healthy"}

    return app
