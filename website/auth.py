from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db
from flask_login import login_user, login_required, logout_user, current_user
from .utils import generate_random_password, has_sql_injection
import os
from dotenv import load_dotenv
import sys

load_dotenv()
auth = Blueprint("auth", __name__)


def validate_admin_password():
    env_password = os.getenv("ADMIN_PASSWORD")
    if not env_password:
        new_password = generate_random_password()
        print("\nWARNING: No admin password found in .env file!")
        print(f"Generated password: {new_password}")
        print(
            "Please add this password to your .env file as ADMIN_PASSWORD=your_password"
        )
        print("Using generated password for now...\n")
        return new_password

    if has_sql_injection(env_password):
        new_password = generate_random_password()
        print("\nWARNING: Admin password in .env contains forbidden characters!")
        print(f"Suggested safe password: {new_password}")
        print("Please update your .env file with a safe password")
        print("Using generated password for now...\n")
        return new_password

    return env_password


def is_admin_exists():
    admin_user = User.query.filter_by(name="admin").first()
    return admin_user


def create_admin():
    admin_password = validate_admin_password()
    new_admin_user = User(
        name="admin",
        password=generate_password_hash(admin_password, method="scrypt"),
        is_active=True,
        is_admin=True,
    )
    db.session.add(new_admin_user)
    db.session.commit()
    print(f"\nAdmin user created successfully!")


@auth.route("/login", methods=["GET", "POST"])
def login():
    if not is_admin_exists():
        create_admin()

    if request.method == "POST":
        name = request.form.get("name")
        password = request.form.get("password")
        remember = request.form.get("remember-me")
        remember_value = True if remember == "on" else False

        if (
            not name
            or not password
            or has_sql_injection(name)
            or has_sql_injection(password)
        ):
            flash("Invalid form.", category="error")
            return redirect(url_for("auth.login"))

        user = User.query.filter_by(name=name).first()
        if user:
            if not user.is_active:
                flash(
                    "This account has been deactivated. Contact administrator.",
                    category="error",
                )
            elif check_password_hash(user.password, password):
                flash("Logged in successfully!", category="success")
                login_user(user, remember=remember_value)
                return redirect(url_for("routes.home"))
            else:
                flash("Incorrect password, try again.", category="error")
        else:
            flash("Name does not exist.", category="error")

    return render_template("login.html", user=current_user)


@auth.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("auth.login"))
