"""
This module contains the routes for managing user coverletters.
"""

from flask import Blueprint, jsonify, request
from models import Users
from utils import get_userid_from_header

coverletter_bp = Blueprint("coverletter", __name__)

@coverletter_bp.route("/coverletters", methods=["POST"])
def create_coverletter():
    """
    Creates a new cover letter for the user.
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        data = request.json

        if not data or "content" not in data:
            return jsonify({"error": "Cover letter content is required"}), 400

        coverletter = {"content": data["content"], "title": data.get("title", "Untitled")}
        user.coverletters.append(coverletter)
        user.save()

        return jsonify({"message": "Cover letter created successfully"}), 201
    except KeyError as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@coverletter_bp.route("/coverletters", methods=["GET"])
def get_all_coverletters():
    """
    Retrieves all cover letters for the user.
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()

        filenames = [
            coverletter["title"] or f"coverletter_{index}" for index, coverletter in enumerate(user.coverletters)
        ]
        return jsonify({"filenames": filenames})
    except KeyError as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@coverletter_bp.route("/coverletters/<int:coverletter_idx>", methods=["GET"])
def get_coverletter(coverletter_idx):
    """
    Retrieves a specific cover letter by index.
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()

        if coverletter_idx >= len(user.coverletters):
            return jsonify({"error": "Cover letter not found"}), 404

        return jsonify({"coverletter": user.coverletters[coverletter_idx]}), 200
    except KeyError as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@coverletter_bp.route("/coverletters/<int:coverletter_idx>", methods=["PUT"])
def update_coverletter(coverletter_idx):
    """
    Updates a specific cover letter by index.
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        data = request.json

        if coverletter_idx >= len(user.coverletters):
            return jsonify({"error": "Cover letter not found"}), 404

        if not data or "content" not in data:
            return jsonify({"error": "Cover letter content is required"}), 400

        user.coverletters[coverletter_idx]["content"] = data["content"]
        user.coverletters[coverletter_idx]["title"] = data.get("title", user.coverletters[coverletter_idx]["title"])
        user.save()

        return jsonify({"message": "Cover letter updated successfully"}), 200
    except KeyError as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500


@coverletter_bp.route("/coverletters/<int:coverletter_idx>", methods=["DELETE"])
def delete_coverletter(coverletter_idx):
    """
    Deletes a specific cover letter by index.
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()

        if coverletter_idx >= len(user.coverletters):
            return jsonify({"error": "Cover letter not found"}), 404

        del user.coverletters[coverletter_idx]
        user.save()

        return jsonify({"message": "Cover letter deleted successfully"}), 200
    except KeyError as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
