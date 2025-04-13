"""
This module contains the routes for managing user profiles.
"""

import json
from flask import Blueprint, jsonify, request
from models import Users, Profile
from utils import get_userid_from_header

profile_bp = Blueprint("profile", __name__)

@profile_bp.route("/getProfile", methods=["GET"])
@profile_bp.route("/getProfile/<int:profileid>", methods=["GET"])
def get_profile_data(profileid=None):
    """Gets Profile Data"""
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        if profileid is not None:
            if profileid < 0 or profileid >= len(user.profiles):
                return jsonify({"error": "Invalid profile ID"}), 400
            selected_profile = user.profiles[profileid]
        else:
            selected_profile = user.profiles[user.default_profile] if user.profiles else None
        if not selected_profile:
            return jsonify({"error": "No profile available"}), 404
        profile_information = {
            "skills": selected_profile.skills,
            "job_levels": selected_profile.job_levels,
            "locations": selected_profile.locations,
            "institution": selected_profile.institution,
            "phone_number": selected_profile.phone_number,
            "address": selected_profile.address,
            "email": user.email,
            "fullName": user.fullName,
            "profileName": selected_profile.profileName,
            "profileid": profileid if profileid is not None else user.default_profile
        }
        return jsonify(profile_information), 200
    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500

@profile_bp.route("/updateProfile", methods=["POST"])
@profile_bp.route("/updateProfile/<int:profileid>", methods=["POST"])
def update_profile(profileid=None):
    """""Updates Profile Data"""
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404
        data = json.loads(request.data)
        if profileid is not None:
            if profileid < 0 or profileid >= len(user.profiles):
                return jsonify({"error": "Invalid profile ID"}), 400
            selected_profile = user.profiles[profileid]
        else:
            if not user.profiles:
                selected_profile = Profile()
                user.profiles.append(selected_profile)
            else:
                selected_profile = user.profiles[user.default_profile]
        for key in data.keys():
            if hasattr(selected_profile, key):
                setattr(selected_profile, key, data[key])
            elif hasattr(user, key):
                setattr(user, key, data[key])
            else:
                return jsonify({"error": f"Invalid field: {key}"}), 400
        user.save()
        return jsonify(user.to_json()), 200
    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500

@profile_bp.route("/createProfile", methods=["POST"])
def create_profile():
    """Creates a new profile for the user"""
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        data = json.loads(request.data)
        new_profile = Profile()

        for key in data.keys():
            if hasattr(new_profile, key):
                setattr(new_profile, key, data[key])
            else:
                return jsonify({"error": f"Invalid field: {key}"}), 400

        user.profiles.append(new_profile)
        user.save()

        return jsonify({
            "message": "Profile created successfully",
            "profileid": len(user.profiles) - 1
        }), 201
    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500

@profile_bp.route("/setDefaultProfile/<int:profileid>", methods=["POST"])
def set_default_profile(profileid):
    """Sets the default profile for the user"""
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        if profileid < 0 or profileid >= len(user.profiles):
            return jsonify({"error": "Invalid profile ID"}), 400

        user.default_profile = profileid
        user.save()

        return jsonify({
            "message": "Default profile updated successfully",
            "default_profile": profileid
        }), 200
    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500

@profile_bp.route("/getProfileList", methods=["GET"])
def get_profile_list():
    """Gets the list of profiles for the user"""
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        if not user:
            return jsonify({"error": "User not found"}), 404

        profile_list = []
        for idx, profile in enumerate(user.profiles):
            profile_info = {
                "profileid": idx,
                "profileName": profile.profileName,
                "isDefault": idx == user.default_profile
            }
            profile_list.append(profile_info)

        return jsonify({
            "profiles": profile_list,
            "default_profile": user.default_profile
        }), 200
    except json.JSONDecodeError as err:
        print(err)
        return jsonify({"error": "Internal server error"}), 500
