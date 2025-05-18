from datetime import datetime, date, time
from . import db
from flask_login import UserMixin


class Case(db.Model):
    __tablename__ = "cases"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(100), nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, unique=True)
    notes = db.relationship("Note", backref="case", lazy=True)
    files = db.relationship("CaseFile", backref="case", lazy=True)
    # Новое поле - связь с создателем дела
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


class Court(db.Model):
    __tablename__ = "courts"
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    address = db.Column(db.String(100), nullable=False)
    notes = db.relationship("Note", backref="court", lazy=True)


class Note(db.Model):
    __tablename__ = "notes"
    id = db.Column(db.Integer, primary_key=True)
    client_name = db.Column(db.String(100), nullable=False)
    case_title = db.Column(db.String(100), nullable=False)
    court_address = db.Column(db.String(100), nullable=False)
    court_name = db.Column(db.String(100), nullable=False)
    details = db.Column(db.String(100), nullable=True)
    date = db.Column(db.Date, nullable=False)
    time = db.Column(db.Time, nullable=False)
    status = db.Column(db.String(50), nullable=False)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
    court_id = db.Column(db.Integer, db.ForeignKey("courts.id"), nullable=False)
    # Добавим поле для связи с создателем
    creator_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True)
    email = db.Column(db.String(150), unique=True, nullable=True)
    password = db.Column(db.String(150))
    is_active = db.Column(db.Boolean, default=True)
    is_admin = db.Column(db.Boolean, default=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)
    # Обратная связь с делами, созданными пользователем
    created_cases = db.relationship("Case", backref="creator", lazy=True, foreign_keys=[Case.creator_id])
    # Обратная связь с заметками, созданными пользователем
    created_notes = db.relationship("Note", backref="creator", lazy=True, foreign_keys=[Note.creator_id])


class CaseFile(db.Model):
    __tablename__ = "case_files"
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    original_filename = db.Column(db.String(255), nullable=False)
    file_size = db.Column(db.Integer, nullable=False)  # Size in bytes
    upload_date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    case_id = db.Column(db.Integer, db.ForeignKey("cases.id"), nullable=False)
