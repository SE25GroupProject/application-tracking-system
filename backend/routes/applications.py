"""
This module contains the routes for managing applications.
"""

from flask import Blueprint, jsonify, request
import json
from models import Users, get_new_application_id
from utils import get_userid_from_header

applications_bp = Blueprint("applications", __name__)


@applications_bp.route("/applications", methods=["GET"])
def get_data():
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        applications = user["applications"]
        return jsonify(applications)
    except:
        return jsonify({"error": "Internal server error"}), 500


@applications_bp.route("/applications", methods=["POST"])
def add_application():
    try:
        userid = get_userid_from_header()
        request_data = json.loads(request.data)["application"]
        try:
            assert "jobTitle" in request_data
            assert "companyName" in request_data
        except:
            return jsonify({"error": "Missing fields in input"}), 400

        user = Users.objects(id=userid).first()
        current_application = {
            "id": get_new_application_id(userid),
            "jobTitle": request_data["jobTitle"],
            "companyName": request_data["companyName"],
            "date": request_data.get("date"),
            "jobLink": request_data.get("jobLink"),
            "location": request_data.get("location"),
            "status": request_data.get("status", "1"),
        }
        applications = user["applications"] + [current_application]
        user.update(applications=applications)
        return jsonify(current_application), 200
    except:
        return jsonify({"error": "Internal server error"}), 500


@applications_bp.route("/applications/<int:application_id>", methods=["PUT"])
def update_application(application_id):
    try:
        userid = get_userid_from_header()
        request_data = json.loads(request.data)["application"]
        user = Users.objects(id=userid).first()
        current_applications = user["applications"]

        if len(current_applications) == 0:
            return jsonify({"error": "No applications found"}), 400
        else:
            updated_applications = []
            app_to_update = None
            application_updated_flag = False
            for application in current_applications:
                if application["id"] == application_id:
                    app_to_update = application
                    application_updated_flag = True
                    for key, value in request_data.items():
                        application[key] = value
                updated_applications += [application]
            if not application_updated_flag:
                return jsonify({"error": "Application not found"}), 400
            user.update(applications=updated_applications)

        return jsonify(app_to_update), 200
    except:
        return jsonify({"error": "Internal server error"}), 500


@applications_bp.route("/applications/<int:application_id>", methods=["DELETE"])
def delete_application(application_id):
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        current_applications = user["applications"]

        application_deleted_flag = False
        updated_applications = []
        app_to_delete = None
        for application in current_applications:
            if application["id"] != application_id:
                updated_applications += [application]
            else:
                app_to_delete = application
                application_deleted_flag = True

        if not application_deleted_flag:
            return jsonify({"error": "Application not found"}), 400
        user.update(applications=updated_applications)
        return jsonify(app_to_delete), 200
    except:
        return jsonify({"error": "Internal server error"}), 500
