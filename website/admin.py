from flask import Blueprint, render_template, request, flash, redirect, url_for, jsonify
from flask_login import login_required, current_user
from .models import User
from . import db
from werkzeug.security import generate_password_hash
from .utils import (
    has_sql_injection,
    is_valid_range,
    generate_random_password,
    is_valid_email,
    admin_required,
)
import json


import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

admin = Blueprint("admin", __name__)


def send_credentials_email(email, username, password):
    try:

        smtp_server = os.getenv("SMTP_SERVER", "smtp.example.com")
        smtp_port = int(os.getenv("SMTP_PORT", 465))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        sender_email = os.getenv("SENDER_EMAIL", "noreply@example.com")

        if not smtp_username or not smtp_password:
            return False, "SMTP credentials not configured"

        print(f"SMTP Settings: {smtp_server}:{smtp_port}, User: {smtp_username}")

        message = MIMEMultipart()
        message["From"] = sender_email
        message["To"] = email
        message["Subject"] = "Your new account credentials"

        body = f"""
        <html>
        <body>
            <h2>Welcome to Case Management System</h2>
            <p>Your account has been created. Here are your credentials:</p>
            <p><strong>Username:</strong> {username}</p>
            <p><strong>Password:</strong> {password}</p>
            <p>Please login and change your password immediately.</p>
            <p>This is an automated message, please do not reply.</p>
        </body>
        </html>
        """

        message.attach(MIMEText(body, "html"))

        print(f"Connecting to SMTP server {smtp_server}:{smtp_port} via SSL...")
        server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        server.set_debuglevel(1)

        print(f"Authenticating as {smtp_username}...")
        server.login(smtp_username, smtp_password)

        print("Sending message...")
        server.sendmail(sender_email, email, message.as_string())
        server.quit()

        print("Message sent successfully!")

        return True, "Email sent successfully"
    except Exception as e:
        print(f"Error sending email: {e}")
        return False, str(e)


@admin.route("/view-users", methods=["GET"])
@login_required
@admin_required
def view_users():
    try:
        users = User.query.all()
        return render_template("view-users.html", user=current_user, users=users)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@admin.route("/create-user", methods=["GET", "POST"])
@login_required
@admin_required
def create_user():
    try:
        if request.method == "POST":
            email = request.form.get("email")

            if (
                not email
                or not is_valid_range(email, 150)
                or has_sql_injection(email)
                or not is_valid_email(email)
            ):
                flash("Invalid email format.", category="error")
                return render_template("create-user.html", user=current_user)

            existing_user = User.query.filter_by(email=email).first()
            if existing_user:
                flash("User with this email already exists.", category="error")
                return render_template("create-user.html", user=current_user)

            username = email.split("@")[0]

            existing_name = User.query.filter_by(name=username).first()
            counter = 1
            original_username = username

            while existing_name:
                username = f"{original_username}{counter}"
                existing_name = User.query.filter_by(name=username).first()
                counter += 1

            password = generate_random_password()

            new_user = User(
                name=username,
                email=email,
                password=generate_password_hash(password, method="scrypt"),
                is_active=True,
                is_admin=False,
            )

            db.session.add(new_user)
            db.session.commit()

            success, message = send_credentials_email(email, username, password)

            if success:
                flash(
                    f"User created successfully! Credentials sent to {email}.",
                    category="success",
                )
            else:
                flash(
                    f"User created but failed to send email: {message}",
                    category="warning",
                )

            return redirect(url_for("admin.view_users"))

        return render_template("create-user.html", user=current_user)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@admin.route("/toggle-user-status", methods=["POST"])
@login_required
@admin_required
def toggle_user_status():
    try:
        data = json.loads(request.data)
        user_id = data["user_id"]
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.id == current_user.id:
            return jsonify({"error": "You cannot modify your own account"}), 400

        user.is_active = not user.is_active
        db.session.commit()

        action = "activated" if user.is_active else "deactivated"
        return (
            jsonify(
                {"message": f"User {action} successfully", "is_active": user.is_active}
            ),
            200,
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@admin.route("/delete-user", methods=["POST"])
@login_required
@admin_required
def delete_user():
    try:
        data = json.loads(request.data)
        user_id = data["user_id"]
        user = User.query.get(user_id)

        if not user:
            return jsonify({"error": "User not found"}), 404

        if user.id == current_user.id:
            return jsonify({"error": "You cannot delete your own account"}), 400

        db.session.delete(user)
        db.session.commit()

        return jsonify({"message": "User deleted successfully"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500
