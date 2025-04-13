"""
This module initializes the shared MongoEngine instance for the application.
"""

from flask_mongoengine import MongoEngine

db: MongoEngine = MongoEngine()
