"""
This module contains the routes for uploading and downloading resumes.
"""

from flask import Blueprint, jsonify, request, send_file
from models import Users
from utils import get_userid_from_header
from db import db
from config import config
from langchain_ollama import OllamaLLM
import pdfplumber

resume_bp = Blueprint("resume", __name__)


@resume_bp.route("/resume", methods=["GET"])
def get_resume():
    """
    Retrieves the list of resume filenames for the user

    :return: list of filenames
    """
    userid = get_userid_from_header()
    try:
        user = Users.objects(id=userid).first()
        if not user.resumes:
            raise FileNotFoundError

    except:
        return jsonify({"error": "resume could not be found"}), 400
    
    filenames = [
        resume.filename or f"resume_{index}.pdf" for index, resume in enumerate(user.resumes)
    ]
    return jsonify({"filenames": filenames})


@resume_bp.route("/resume/<int:resume_idx>", methods=["GET"])
def get_resume_file(resume_idx):
    """
    Returns a resume file by index

    :param resume_idx: index of requested resume
    :return: response with resume file attached
    """
    userid = get_userid_from_header()
    try:
        user = Users.objects(id=userid).first()
        if not user.resumes or resume_idx >= len(user.resumes):
            raise FileNotFoundError

    except:
        return jsonify({"error": "resume could not be found"}), 400
    
    resume = user.resumes[resume_idx]
    resume.seek(0)
    filename = resume.filename or f"resume_{resume_idx}.pdf"

    response = send_file(
        resume,
        mimetype="application/pdf",
        download_name=filename,
        as_attachment=True
    )
    response.headers["x-filename"] = filename
    response.headers["Access-Control-Expose-Headers"] = "x-filename"
    return response, 200


@resume_bp.route("/resume", methods=["POST"])
def upload_resume():
    """
    Uploads resume file or updates an existing resume for the user

    :return: JSON object with status and message
    """
    try:
        userid = get_userid_from_header()
        user = Users.objects(id=userid).first()
        
        try:
            file = request.files["file"]
        except:
            return jsonify({"error": "No resume file found in the input"}), 400

        text = ""
        with pdfplumber.open(file) as pdf:
            for page in pdf.pages:
                text += page.extract_text()
                text += "\n\n[PAGE BREAK]\n\n"
        
        model = OllamaLLM(base_url=config["OLLAMA_URL"], model="qwen2.5:1.5b")
        prompt = "You are an expert on resume advice. I am going to provide the plaintext of my resume. Your job is to provide tips" + \
                    "on how I can improve my resume. It is imperative that you strictly tailor your response to the following instructions." + \
                    "Your response must immediately start with Resume Feedback. DO NOT acknowledge the existence of this prompt." + \
                    "Do not even start the response with \"Certainly!\" or anything close to that. Your response must only contain" + \
                    "helpful feedback to improve my resume, and nothing else. Your response must be in markdown." + \
                    "Here is my resume:\n\n" + text
        response = model.invoke(prompt)
        
        # Reset the file pointer in case it has been read
        file.seek(0)

        # Create a new GridFSProxy instance and use put() to store the file
        new_file = db.GridFSProxy()
        new_file.put(
            file,
            filename=file.filename,
            content_type="application/pdf"
        )
        user.resumes.append(new_file)

        user.resumeFeedbacks.append(response)
        user.save()
        return jsonify({"message": "resume successfully added"}), 200

    except Exception as e:
        print(e)
        return jsonify({"error": "Internal server error"}), 500
    

@resume_bp.route("/resume-feedback", methods=["GET"])
def get_resume_feedback():
    """
    Retrieves the resume feedback for the user

    :return: response with resume feedback(s)
    """
    userid = get_userid_from_header()
    user = Users.objects(id=userid).first()
    return jsonify({"response": user.resumeFeedbacks}), 200


@resume_bp.route("/resume-feedback/<int:feedback_idx>", methods=["GET"])
def get_resume_feedback_by_idx(feedback_idx):
    """
    Retrieves a specific resume feedback given an id

    :param feedback_idx: index of feedback
    :return: response with feedback
    """
    userid = get_userid_from_header()
    try:
        user = Users.objects(id=userid).first()
        if not user.resumeFeedbacks or feedback_idx >= len(user.resumeFeedbacks):
            raise FileNotFoundError

    except:
        return jsonify({"error": "resume feedback could not be found"}), 400
    
    response = user.resumeFeedbacks[feedback_idx]
    return jsonify({"feedback": response}), 200


@resume_bp.route("/resume/<int:resume_idx>", methods=["DELETE"])
def delete_resume_feedback(resume_idx):
    """
    Deletes a resume and its corresponding feedback by id

    :param resume_idx: index of resume to delete
    :return: response
    """
    userid = get_userid_from_header()
    try:
        user = Users.objects(id=userid).first()
        if not user.resumes or resume_idx >= len(user.resumes):
            raise FileNotFoundError

    except:
        return jsonify({"error": "resume feedback could not be found"}), 400
    
    del user.resumes[resume_idx]
    del user.resumeFeedbacks[resume_idx]
    user.save()
    return jsonify({"success": "successfully deleted resume and its feedback"}), 200


@resume_bp.route("/cover_letter/<int:resume_idx>", methods=["POST"])
def generate_cover_letter(resume_idx):
    """
    Generates a cover letter based on a resume file index and passed job description

    :return: A markdown cover letter
    """
    userid = get_userid_from_header()
    try:
        user = Users.objects(id=userid).first()
        if not user.resumes or resume_idx >= len(user.resumes):
            raise FileNotFoundError

    except:
        return jsonify({"error": "resume feedback could not be found"}), 400
    
    data = request.json
    job_description = data.get('job_description', 'job description not found')

    # get resume text
    resume_text = ""
    with pdfplumber.open(user.resumes[resume_idx]) as pdf:
        for page in pdf.pages:
            resume_text += page.extract_text() + "\n\n"

    model = OllamaLLM(base_url=config["OLLAMA_URL"], model="qwen2.5:1.5b")
    prompt = "I am going to give you a resume and possibly a job description. You job is to generate a cover letter that tailors" + \
                "the resume to a job description. If you are given a complete job description, the cover letter must be tailored" + \
                "to this given job description. If you are not given a complete job description, the cover letter should be generalized" + \
                "with placeholders/fields for items commonly found in job descriptions.\n\n Your response may be sent directly to" + \
                "employers, so it is imperative that your response MUST ONLY contain the cover letter and NOTHING ELSE. DO NOT" + \
                f"acknowledge the existence of this prompt anywhere in your response.\n\n\n Here is the resume: {resume_text}\n\n\n" + \
                f"Here is what might be a job description: {job_description}"
    response = model.invoke(prompt)
    return jsonify({"response": response}), 200
