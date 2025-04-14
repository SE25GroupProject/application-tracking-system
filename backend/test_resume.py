"""
Test module for resume-related endpoints (Tests 9-29)
"""

import hashlib
from io import BytesIO

import json
import pytest
from app import create_app
from models import Users


@pytest.fixture()
def app():
    """
    Fixture to create a test instance of the Flask application.

    Returns:
        Flask: The configured Flask application instance.
    """
    app = create_app()
    return app


@pytest.fixture
def client(app):
    """
    Fixture to provide a test client for the Flask application.

    Args:
        app: The Flask application instance provided by the app fixture.

    Yields:
        FlaskClient: The test client for making HTTP requests.
    """
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture
def user(client):
    """
    Fixture to create a test user and authenticate them.

    Args:
        client: The Flask test client provided by the client fixture.

    Yields:
        tuple: A tuple containing the user object and authentication header.
    """
    data = {"username": "testUser", "password": "test", "fullName": "fullName"}
    user = Users(
        id=1,
        fullName=data["fullName"],
        username=data["username"],
        password=hashlib.md5(data["password"].encode()).hexdigest(),
        authTokens=[],
        email="",
        applications=[],
        resumes=[],
        coverletters=[],
        resumeFeedbacks=[],
        profiles=[],
        default_profile=0
    )
    user.save()
    rv = client.post("/users/login", json=data)
    jdata = json.loads(rv.data.decode("utf-8"))
    header = {"Authorization": "Bearer " + jdata["token"]}
    yield user, header
    user.delete()


# Test 9: Resume Upload (Text File)
def test_resume(client, mocker, user):
    """
    Test uploading a text file as a resume, expecting failure.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.resumes = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing resume"), "resume.txt"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 500


# Test 10: Resume Upload (PDF)
def test_resume_pdf(client, mocker, user):
    """
    Test uploading a PDF resume.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    # Mock the user ID
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )

    user, header = user
    user.applications = []
    user.resumes = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200


# Test 11: Resume Retrieval (Non-existent)
def test_resume_dne(client, mocker, user):
    """
    Test retrieving a resume when none exists.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.resumes = []
    user.save()
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 400


# Test 12: Resume Upload (Non-PDF)
def test_resume_non_pdf(client, mocker, user):
    """
    Test uploading a non-PDF file as a resume and retrieving resumes.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.resumes = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing resume that is not the expected file type"), "resume.txt"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 500
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 400


# Test 13: Resume Feedback (Non-existent)
def test_resume_feedback_dne(client, mocker, user):
    """
    Test retrieving resume feedback when none exists.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 0


# Test 14: Resume Feedback (Valid)
def test_resume_feedback(client, mocker, user):
    """
    Test retrieving resume feedback after uploading a valid PDF resume.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 1


# Test 15: Resume Feedback by Index
def test_resume_feedback_by_idx(client, mocker, user):
    """
    Test retrieving resume feedback by specific index after uploading a PDF.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback/0", headers=header)
    assert rv.status_code == 200


# Test 16: Resume Feedback by Invalid High Index
def test_resume_feedback_by_idx_invalid_too_high(client, mocker, user):
    """
    Test retrieving resume feedback with an invalid high index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback/3", headers=header)
    assert rv.status_code == 400


# Test 17: Resume Feedback by Invalid Negative Index
def test_resume_feedback_by_idx_invalid_negative(client, mocker, user):
    """
    Test retrieving resume feedback with a negative index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback/-1", headers=header)
    assert rv.status_code == 404


# Test 18: Resume Deletion
def test_resume_delete(client, mocker, user):
    """
    Test deleting a resume by index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# Test 19: Resume Deletion (Invalid Index)
def test_resume_delete_invalid(client, mocker, user):
    """
    Test deleting a resume with an invalid index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/2", headers=header)
    assert rv.status_code == 400


# Test 20: Resume Deletion (Non-existent)
def test_resume_delete_dne(client, mocker, user):
    """
    Test deleting a non-existent resume.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    rv = client.delete("/resume/2", headers=header)
    assert rv.status_code == 400


# Test 21: Resume Upload (Alternate PDF)
def test_resume_pdf_2(client, mocker, user):
    """
    Test uploading an alternate PDF resume and retrieving it.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200


# Test 22: Multiple Resume Upload
def test_resume_pdf_multiple(client, mocker, user):
    """
    Test uploading multiple PDF resumes and retrieving them.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200


# Test 23: Multiple Resume Feedback
def test_resume_pdf_multiple_feedback(client, mocker, user):
    """
    Test retrieving feedback for multiple uploaded resumes.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 2


# Test 24: Multiple Resume Feedback by Index (First)
def test_resume_pdf_multiple_feedback_by_idx(client, mocker, user):
    """
    Test retrieving feedback for the first of multiple uploaded resumes by index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback/0", headers=header)
    assert rv.status_code == 200


# Test 25: Multiple Resume Feedback by Index (Second)
def test_resume_pdf_multiple_feedback_by_idx_2(client, mocker, user):
    """
    Test retrieving feedback for the second of multiple uploaded resumes by index.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.get("/resume-feedback/1", headers=header)
    assert rv.status_code == 200


# Test 26: Delete First Resume from Multiple
def test_resume_delete_first(client, mocker, user):
    """
    Test deleting the first resume from multiple uploaded resumes.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# Test 27: Delete Last Resume from Multiple
def test_resume_delete_last(client, mocker, user):
    """
    Test deleting the last resume from multiple uploaded resumes.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/1", headers=header)
    assert rv.status_code == 200


# Test 28: Delete Multiple Resumes
def test_delete_multiple_resumes(client, mocker, user):
    """
    Test deleting multiple resumes sequentially.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# Test 29: Delete Resume with Invalid Index (Multiple)
def test_resume_delete_multiple_invalid(client, mocker, user):
    """
    Test deleting a resume with an invalid index when multiple resumes exist.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
    mocker.patch("models.get_new_user_id", return_value=-1)
    # Mock the OllamaLLM.invoke method to avoid loading the model
    mocker.patch(
        "langchain_ollama.OllamaLLM.invoke",
        return_value="Resume Feedback\n\n- Add more quantifiable achievements.\n- Clarify your job titles."
    )
    user, header = user
    user.applications = []
    user.resumes = []
    user.resumeFeedbacks = []
    user.save()
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())
    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200
    rv = client.delete("/resume/3", headers=header)
    assert rv.status_code == 400
