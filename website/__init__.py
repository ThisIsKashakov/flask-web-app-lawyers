import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv


basedir = path.abspath(path.dirname(__file__))


env_path = path.join(basedir, "..", ".env")


if not os.path.exists(env_path):
    print(
        "Error: `.env` file not found. Please create it based on `.env.example` and fill in the variables."
    )
    sys.exit(1)


load_dotenv(env_path)


secret = os.getenv("SECRET_KEY")
if not secret:

    import secrets

    new_key = secrets.token_hex(32)
    print("Warning: No SECRET_KEY found in `.env`.")
    print(f"Generated a new SECRET_KEY: {new_key}")
    print(
        "Please copy this value into your `.env` as SECRET_KEY=<generated_key> and restart the application."
    )
    sys.exit(1)


db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)

    app.config["SECRET_KEY"] = secret

    app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{DB_NAME}"
    db.init_app(app)

    from .routes import routes
    from .auth import auth
    from .admin import admin

    app.register_blueprint(routes, url_prefix="/")
    app.register_blueprint(auth, url_prefix="/")
    app.register_blueprint(admin, url_prefix="/")

    from .models import User

    with app.app_context():
        db.create_all()

    login_manager = LoginManager()
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))

    return app


def create_database(app):
    if not path.exists("website/" + DB_NAME):
        db.create_all(app=app)
        print("Created Database!")
