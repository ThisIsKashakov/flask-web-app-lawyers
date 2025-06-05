from flask import Blueprint, render_template, request, flash, jsonify, redirect, url_for
from flask_login import login_required, current_user
from . import db
from .models import Case, Court, Note
from .utils import (
    has_sql_injection,
    is_number,
    is_valid_range,
    is_valid_date,
    is_valid_time,
    allowed_file,
    is_file_size_allowed,
    get_storage_stats,
    is_storage_available,
    STORAGE_LIMIT,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE,
    admin_required,
)
import json
from sqlalchemy.orm import joinedload
from sqlalchemy import or_
from datetime import datetime, date, time

from werkzeug.utils import secure_filename
from datetime import datetime
from .models import CaseFile
from flask import send_file
import os

routes = Blueprint("routes", __name__)

UPLOAD_FOLDER = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "uploads"
)


os.makedirs(UPLOAD_FOLDER, exist_ok=True)


@routes.route("/", methods=["GET"])
@login_required
def home():
    try:
        notes = Note.query.all()
        return render_template("home.html", user=current_user, notes=notes)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/search", methods=["POST"])
@login_required
def search():
    try:
        search_query = request.form.get("search")
        notes = Note.query.filter(
            or_(
                Note.client_name.ilike(f"%{search_query}%"),
                Note.case_title.ilike(f"%{search_query}%"),
                Note.court_address.ilike(f"%{search_query}%"),
                Note.court_name.ilike(f"%{search_query}%"),
                Note.details.ilike(f"%{search_query}%"),
                Note.date.ilike(f"%{search_query}%"),
                Note.time.ilike(f"%{search_query}%"),
                Note.status.ilike(f"%{search_query}%"),
            )
        ).all()

        return render_template("home.html", user=current_user, notes=notes)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


allowed_status = {"resolved": True, "pending": True, "rejected": True}


@routes.route("/new-note", methods=["GET", "POST"])
@login_required
def new_note():
    try:
        cases = Case.query.all()
        courts = Court.query.all()
        if request.method == "POST":
            case_id = request.form.get("case_id")
            court_id = request.form.get("court_id")
            status = request.form.get("status")
            details = request.form.get("details")
            date_str = request.form.get("date")
            time_str = request.form.get("time")

            if (
                not case_id
                or not is_number(case_id)
                or not court_id
                or not is_number(court_id)
                or not status
                or not allowed_status.get(status)
                or not date_str
                or not is_valid_date(date_str)
                or not time_str
                or not is_valid_time(time_str)
            ):
                flash("Invalid form.", category="error")
            else:
                case = Case.query.get(case_id)
                court = Court.query.get(court_id)
                if not case or not court:
                    flash("Case or Court not found.", category="error")
                    return render_template(
                        "new-note.html", user=current_user, cases=cases, courts=courts
                    )

                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                time = datetime.strptime(time_str, "%H:%M").time()

                new_note = Note(
                    client_name=case.full_name,
                    case_title=case.title,
                    court_address=court.address,
                    court_name=court.title,
                    details=details,
                    date=date,
                    time=time,
                    status=status,
                    case_id=case_id,
                    court_id=court_id,
                    creator_id=current_user.id,
                )
                db.session.add(new_note)
                db.session.commit()
                flash("Note created!", category="success")
        return render_template(
            "new-note.html", user=current_user, cases=cases, courts=courts
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/edit-note/<int:id>", methods=["GET", "POST"])
@login_required
def edit_note(id):
    try:
        cases = Case.query.all()
        courts = Court.query.all()
        note = Note.query.get(id)
        if not note:
            return redirect(url_for("routes.view_courts"))

        if not current_user.is_admin and note.creator_id != current_user.id:
            flash("You don't have permission to edit this note.", category="error")
            return redirect(url_for("routes.home"))

        if request.method == "POST":
            case_id = request.form.get("case_id")
            court_id = request.form.get("court_id")
            status = request.form.get("status")
            details = request.form.get("details")
            date_str = request.form.get("date")
            time_str = request.form.get("time")
            print(status)
            print(time_str)

            if (
                not case_id
                or not is_number(case_id)
                or not court_id
                or not is_number(court_id)
                or not status
                or not allowed_status.get(status)
                or not date_str
                or not is_valid_date(date_str)
                or not time_str
                or not is_valid_time(time_str)
            ):
                flash("Invalid form.", category="error")
            else:
                case = Case.query.get(case_id)
                court = Court.query.get(court_id)
                if not case or not court:
                    flash("Case or Court not found.", category="error")
                    return render_template(
                        "edit-note.html",
                        user=current_user,
                        note=note,
                        cases=cases,
                        courts=courts,
                    )

                date = datetime.strptime(date_str, "%Y-%m-%d").date()
                try:
                    time = datetime.strptime(time_str, "%H:%M:%S").time()
                except ValueError:
                    time = datetime.strptime(time_str, "%H:%M").time()

                note.client_name = case.full_name
                note.case_title = case.title
                note.court_address = court.address
                note.court_name = court.title
                note.details = details
                note.date = date
                note.time = time
                note.status = status
                note.case_id = case_id
                note.court_id = court_id
                db.session.commit()
                flash("Note edited!", category="success")
                return redirect(url_for("routes.view_courts"))

        return render_template(
            "edit-note.html", user=current_user, note=note, cases=cases, courts=courts
        )
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/delete-note", methods=["POST"])
@login_required
def delete_note():
    try:
        data = json.loads(request.data)
        note_id = data["id"]
        note = Note.query.get(note_id)
        if not note:
            return jsonify({"error": "Note not found"}), 404

        if not current_user.is_admin and note.creator_id != current_user.id:
            return (
                jsonify({"error": "You don't have permission to delete this note"}),
                403,
            )

        db.session.delete(note)
        db.session.commit()
        flash("Note deleted!", category="success")
        return jsonify({"message": "Note deleted successfully"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/view-cases", methods=["GET"])
@login_required
def view_cases():
    try:

        cases = Case.query.all()
        return render_template("view-cases.html", user=current_user, cases=cases)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/search-cases", methods=["POST"])
@login_required
def search_cases():
    try:
        print("view search cases!")
        search_query = request.form.get("search")
        cases = Case.query.filter(
            or_(
                Case.id.ilike(f"%{search_query}%"),
                Case.title.ilike(f"%{search_query}%"),
                Case.details.ilike(f"%{search_query}%"),
                Case.full_name.ilike(f"%{search_query}%"),
                Case.phone.ilike(f"%{search_query}%"),
            )
        ).all()

        return render_template("view-cases.html", user=current_user, cases=cases)

    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/new-case", methods=["GET", "POST"])
@login_required
def new_case():
    try:
        if request.method == "POST":
            title = request.form.get("title")
            details = request.form.get("details")
            full_name = request.form.get("full_name")
            phone = request.form.get("phone")
            case = Case.query.filter_by(full_name=full_name, phone=phone).first()
            if (
                not title
                or not is_valid_range(title, 100)
                or has_sql_injection(title)
                or not details
                or not is_valid_range(details, 100)
                or has_sql_injection(details)
                or not full_name
                or not is_valid_range(full_name, 100)
                or has_sql_injection(full_name)
                or not phone
                or not is_valid_range(phone, 20)
                or has_sql_injection(phone)
            ):
                flash("Invalid form.", category="error")
            elif case:
                flash("Case already exists!", category="error")
            else:
                new_case = Case(
                    title=title,
                    details=details,
                    full_name=full_name,
                    phone=phone,
                    creator_id=current_user.id,
                )
                db.session.add(new_case)
                db.session.commit()
                flash("Case created!", category="success")
        return render_template("new-case.html", user=current_user)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/edit-case/<int:case_id>", methods=["GET", "POST"])
@login_required
def edit_case(case_id):
    try:
        case = Case.query.get(case_id)
        if not case:
            return redirect(url_for("routes.view_cases"))

        if not current_user.is_admin and case.creator_id != current_user.id:
            flash("You don't have permission to edit this case.", category="error")
            return redirect(url_for("routes.view_cases"))

        if request.method == "POST":
            title = request.form.get("title")
            details = request.form.get("details")
            full_name = request.form.get("full_name")
            phone = request.form.get("phone")
            if (
                not title
                or not is_valid_range(title, 100)
                or has_sql_injection(title)
                or not details
                or not is_valid_range(details, 100)
                or has_sql_injection(details)
                or not full_name
                or not is_valid_range(full_name, 100)
                or has_sql_injection(full_name)
                or not phone
                or not is_valid_range(phone, 20)
                or has_sql_injection(phone)
            ):
                flash("Invalid form.", category="error")
            else:
                case.title = title
                case.details = details
                case.full_name = full_name
                case.phone = phone
                db.session.commit()
                flash("Case edited!", category="success")
                return redirect(url_for("routes.view_cases"))
        return render_template("edit-case.html", user=current_user, case=case)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/delete-case", methods=["POST"])
@login_required
def delete_case():
    try:
        case_data = json.loads(request.data)
        case_id = case_data["case_id"]
        case = Case.query.get(case_id)

        if not case:
            return jsonify({"error": "Case not found"}), 404

        if not current_user.is_admin and case.creator_id != current_user.id:
            return (
                jsonify({"error": "You don't have permission to delete this case"}),
                403,
            )

        notes = Note.query.filter_by(case_id=case_id).first()
        if notes:
            return (
                jsonify(
                    {"error": "Case is associated with notes and cannot be deleted"}
                ),
                400,
            )

        db.session.delete(case)
        db.session.commit()
        flash("Case deleted!", category="success")
        print("Case deleted successfully!")

        return jsonify({"message": "Case deleted successfully"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/case-files/<int:case_id>", methods=["GET"])
@login_required
def case_files(case_id):
    case = Case.query.get_or_404(case_id)

    if not current_user.is_admin and case.creator_id != current_user.id:
        flash(
            "Access denied. You don't have permission to view files for this case.",
            category="error",
        )
        return redirect(url_for("routes.view_cases"))

    files = CaseFile.query.filter_by(case_id=case_id).all()
    storage_stats = get_storage_stats(UPLOAD_FOLDER)
    return render_template(
        "case-files.html",
        case=case,
        files=files,
        user=current_user,
        storage_stats=storage_stats,
    )


@routes.route("/upload-file/<int:case_id>", methods=["POST"])
@login_required
def upload_file(case_id):
    try:
        case = Case.query.get_or_404(case_id)

        if not current_user.is_admin and case.creator_id != current_user.id:
            flash(
                "Access denied. You don't have permission to upload files to this case.",
                category="error",
            )
            return redirect(url_for("routes.view_cases"))

        if "file" not in request.files:
            flash("No file part", category="error")
            return redirect(request.url)

        file = request.files["file"]

        if file.filename == "":
            flash("No selected file", category="error")
            return redirect(request.url)

        if not allowed_file(file.filename):
            flash("Invalid file type", category="error")
            return redirect(request.url)

        if not is_file_size_allowed(file, MAX_FILE_SIZE):
            flash("File size exceeds 8MB limit", category="error")
            return redirect(request.url)

        if not is_storage_available(UPLOAD_FOLDER, file.content_length):
            flash("Not enough storage space", category="error")
            return redirect(request.url)

        filename = secure_filename(file.filename)
        unique_filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"

        file.seek(0, 2)
        file_size = file.tell()
        file.seek(0)

        file_path = os.path.join(UPLOAD_FOLDER, unique_filename)
        file.save(file_path)

        new_file = CaseFile(
            filename=unique_filename,
            original_filename=filename,
            file_size=file_size,
            case_id=case_id,
        )
        db.session.add(new_file)
        db.session.commit()

        flash("File uploaded successfully!", category="success")

        return redirect(url_for("routes.case_files", case_id=case_id))
    except Exception as e:
        flash(str(e), category="error")
        return redirect(url_for("routes.case_files", case_id=case_id))


@routes.route("/download-file/<int:file_id>")
@login_required
def download_file(file_id):
    case_file = CaseFile.query.get_or_404(file_id)
    case = Case.query.get_or_404(case_file.case_id)

    if not current_user.is_admin and case.creator_id != current_user.id:
        flash(
            "Access denied. You don't have permission to download this file.",
            category="error",
        )
        return redirect(url_for("routes.view_cases"))

    file_path = os.path.join(UPLOAD_FOLDER, case_file.filename)

    if os.path.exists(file_path):
        return send_file(
            file_path, download_name=case_file.original_filename, as_attachment=True
        )
    else:
        flash("File not found", category="error")
        return redirect(url_for("routes.case_files", case_id=case_file.case_id))


@routes.route("/delete-file/<int:file_id>", methods=["POST"])
@login_required
def delete_file(file_id):
    try:
        case_file = CaseFile.query.get_or_404(file_id)
        case = Case.query.get_or_404(case_file.case_id)

        if not current_user.is_admin and case.creator_id != current_user.id:
            flash(
                "Access denied. You don't have permission to delete this file.",
                category="error",
            )
            return redirect(url_for("routes.view_cases"))

        file_path = os.path.join(UPLOAD_FOLDER, case_file.filename)

        if os.path.exists(file_path):
            os.remove(file_path)

        db.session.delete(case_file)
        db.session.commit()

        flash("File deleted successfully!", category="success")
        return redirect(url_for("routes.case_files", case_id=case_file.case_id))
    except Exception as e:
        flash(str(e), category="error")
        return redirect(url_for("routes.case_files", case_id=case_file.case_id))


@routes.route("/view-courts", methods=["GET", "POST"])
@login_required
def view_courts():
    try:
        courts = Court.query.all()
        return render_template("view-courts.html", user=current_user, courts=courts)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/search-courts", methods=["POST"])
@login_required
def search_courts():
    try:
        search_query = request.form.get("search")
        courts = Court.query.filter(
            or_(
                Court.id.ilike(f"%{search_query}%"),
                Court.title.ilike(f"%{search_query}%"),
                Court.address.ilike(f"%{search_query}%"),
            )
        ).all()

        return render_template("view-courts.html", user=current_user, courts=courts)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/new-court", methods=["GET", "POST"])
@login_required
@admin_required
def new_court():
    try:
        if request.method == "POST":
            title = request.form.get("title")
            address = request.form.get("address")
            court = Court.query.filter_by(title=title).first()
            if (
                not title
                or not is_valid_range(title, 100)
                or has_sql_injection(title)
                or not address
                or not is_valid_range(address, 100)
                or has_sql_injection(address)
            ):
                flash("Invalid form.", category="error")
            elif court:
                flash("Court already exists!", category="error")
            else:
                new_court = Court(title=title, address=address)
                db.session.add(new_court)
                db.session.commit()
                flash("Court created!", category="success")
        return render_template("new-court.html", user=current_user)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/edit-court/<int:id>", methods=["GET", "POST"])
@login_required
@admin_required
def edit_court(id):
    try:
        court = Court.query.get(id)
        if not court:
            return redirect(url_for("routes.home"))
        if request.method == "POST":
            title = request.form.get("title")
            address = request.form.get("address")
            if (
                not title
                or not is_valid_range(title, 100)
                or has_sql_injection(title)
                or not address
                or not is_valid_range(address, 100)
                or has_sql_injection(address)
            ):
                flash("Invalid form.", category="error")
            else:
                court.title = title
                court.address = address
                db.session.commit()
                flash("Court edited!", category="success")
                return redirect(url_for("routes.home"))
        return render_template("edit-court.html", user=current_user, court=court)
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/delete-court", methods=["POST"])
@login_required
@admin_required
def delete_court():
    try:
        court_data = json.loads(request.data)
        court_id = court_data["court_id"]
        court = Court.query.get(court_id)
        if not court:
            return jsonify({"error": "Court not found"}), 404

        notes_associated = Note.query.filter_by(court_id=court_id).first()
        if notes_associated:
            return (
                jsonify(
                    {
                        "error": "Court is associated with case notes and cannot be deleted"
                    }
                ),
                400,
            )

        db.session.delete(court)
        db.session.commit()
        flash("Court deleted!", category="success")
        print("Court deleted successfully!")

        return jsonify({"message": "Court deleted successfully"}), 200
    except Exception as e:
        return jsonify({"Error": str(e)}), 500


@routes.route("/storage-info")
@login_required
def storage_info():
    """Get storage statistics"""
    try:
        stats = get_storage_stats(UPLOAD_FOLDER)
        return jsonify(stats), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
