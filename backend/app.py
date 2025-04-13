"""
The flask application for our program
"""

import os

from flask import Flask, jsonify
from flask_cors import CORS, cross_origin
from authlib.integrations.flask_client import OAuth
from config import config
from db import db
from utils import middleware

from routes.auth import auth_bp
from routes.profile import profile_bp
from routes.applications import applications_bp
from routes.resume import resume_bp
from routes.jobs import jobs_bp



def create_app():
    """
    Creates and initializes the Flask application
    """

    flask_app = Flask(__name__)
    CORS(flask_app)

    # Initialize OAuth
    oauth = OAuth(flask_app)
    auth_bp.oauth = oauth

    db_username = os.getenv("MONGO_INITDB_ROOT_USERNAME", "empty")
    db_password = os.getenv("MONGO_INITDB_ROOT_PASSWORD", "empty")
    db_cluster_url = os.getenv("CLUSTER_URL", "empty")

    # Set configuration
    flask_app.secret_key = config["SECRET_KEY"]
    flask_app.config["MONGODB_SETTINGS"] = {
        "db": "appTracker",
        "host": f"mongodb://{db_username}:{db_password}@{db_cluster_url}/",
    }

    db.init_app(flask_app)

    # Register middleware
    flask_app.before_request(middleware(["/applications", "/resume"]))

    # Register blueprints
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(profile_bp)
    flask_app.register_blueprint(applications_bp)
    flask_app.register_blueprint(resume_bp)
    flask_app.register_blueprint(jobs_bp)

    @flask_app.route("/")
    @cross_origin()
    # pylint: disable=unused-variable
    def health_check():
        return jsonify({"message": "Server up and running"}), 200

    return flask_app


if __name__ == "__main__":
    app = create_app()

    app.run(host="0.0.0.0", port=5000, debug=True)
