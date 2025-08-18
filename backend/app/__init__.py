from flask import Flask
from app.config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    from .routes.main import main
    app.register_blueprint(main)

    return app
