"""
This module contains the routes for managing user profiles.
"""

from flask import Blueprint, jsonify, request
import json
from models import Users
from utils import get_userid_from_header

profile_bp = Blueprint("profile", __name__)


@profile_bp.route("/getProfile", methods=["GET"])
def get_profile_data():
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        profile_information = {
            "skills": user["skills"],
            "job_levels": user["job_levels"],
            "locations": user["locations"],
            "institution": user["institution"],
            "phone_number": user["phone_number"],
            "address": user["address"],
            "email": user["email"],
            "fullName": user["fullName"],
        }
        return jsonify(profile_information)
    except:
        return jsonify({"error": "Internal server error"}), 500


@profile_bp.route("/updateProfile", methods=["POST"])
def update_profile():
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        data = json.loads(request.data)
        for key in data.keys():
            user[key] = data[key]
        user.save()
        return jsonify(user.to_json()), 200
    except Exception as err:
        return jsonify({"error": "Internal server error"}), 500
