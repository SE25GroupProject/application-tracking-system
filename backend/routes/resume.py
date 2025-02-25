"""
This module contains the routes for uploading and downloading resumes.
"""

from flask import Blueprint, jsonify, request, send_file
from models import Users
from utils import get_userid_from_header

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume", methods=["POST"])
def upload_resume():
    try:
        userid = get_userid_from_header()
        file = request.files["file"]
        user = Users.objects(id=userid).first()
        if not user.resume.read():
            user.resume.put(
                file, filename=file.filename, content_type="application/pdf"
            )
            user.save()
            return jsonify({"message": "resume successfully uploaded"}), 200
        else:
            user.resume.replace(
                file, filename=file.filename, content_type="application/pdf"
            )
            user.save()
            return jsonify({"message": "resume successfully replaced"}), 200
    except Exception as e:
        return jsonify({"error": "Internal server error"}), 500


@resume_bp.route("/resume", methods=["GET"])
def get_resume():
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if len(user.resume.read()) == 0:
            raise FileNotFoundError
        else:
            user.resume.seek(0)
        filename = user.resume.filename
        content_type = user.resume.contentType
        response = send_file(
            user.resume,
            mimetype=content_type,
            download_name=filename,
            as_attachment=True,
        )
        response.headers["x-filename"] = filename
        response.headers["Access-Control-Expose-Headers"] = "x-filename"
        return response, 200
    except:
        return jsonify({"error": "Internal server error"}), 500
