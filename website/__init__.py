# website/__init__.py

import os
import sys
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
from dotenv import load_dotenv

# Path to this file’s directory
basedir = path.abspath(path.dirname(__file__))

# Assume .env is one level up (next to main.py)
env_path = path.join(basedir, "..", ".env")

# 1) Check for .env file
if not os.path.exists(env_path):
    print(
        "Error: `.env` file not found. Please create it based on `.env.example` and fill in the variables."
    )
    sys.exit(1)

# 2) Load environment variables from .env
load_dotenv(env_path)

# 3) Check for SECRET_KEY in the loaded variables
secret = os.getenv("SECRET_KEY")
if not secret:
    # If missing, generate a new one, print it out and exit
    import secrets

    new_key = secrets.token_hex(32)
    print("Warning: No SECRET_KEY found in `.env`.")
    print(f"Generated a new SECRET_KEY: {new_key}")
    print(
        "Please copy this value into your `.env` as SECRET_KEY=<generated_key> and restart the application."
    )
    sys.exit(1)

# If we reach this point, .env exists and SECRET_KEY is set. Continue initialization:

db = SQLAlchemy()
DB_NAME = "database.db"


def create_app():
    app = Flask(__name__)

    # Use SECRET_KEY from environment (we already ensured it exists)
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
