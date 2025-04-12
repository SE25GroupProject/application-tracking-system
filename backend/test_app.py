"""
Test module for the backend
"""

import hashlib
from io import BytesIO

import pytest
import json
import datetime
from app import create_app
from models import Users, Profile


@pytest.fixture()
def app():
    app = create_app()
    return app


@pytest.fixture
def client(app):
    client = app.test_client()
    ctx = app.app_context()
    ctx.push()
    yield client
    ctx.pop()


@pytest.fixture
def user(client):
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


# Test 1: Server Status
def test_alive(client):
    rv = client.get("/")
    assert rv.data.decode("utf-8") == '{\n  "message": "Server up and running"\n}\n'


# Test 2: Search Endpoint
def test_search(client, mocker):
    # Mock the Selenium WebDriver
    mock_driver = mocker.patch("selenium.webdriver.Remote")
    
    # Create a mock for div.data-details to handle nested span elements
    mock_details = mocker.Mock()
    mock_details.find_element.side_effect = lambda by, value: mocker.Mock(
        text={
            "span:nth-child(1)": "Tech Corp",
            "span:nth-child(2)": "New York, NY",
            "span:nth-child(3)": "Full-time",
        }[value]
    )
    
    # Mock a single job listing
    mock_job = mocker.Mock()
    mock_job.find_element.side_effect = lambda by, value: {
        "div.data-results-title": mocker.Mock(text="Software Engineer"),
        "div.data-details": mock_details,
        "a.data-results-content": mocker.Mock(get_attribute=lambda *args: "https://www.careerbuilder.com/job/123"),
    }[value]
    
    # Configure find_elements to return the mock job
    mock_driver.return_value.__enter__.return_value.find_elements.return_value = [mock_job]
    
    # Send request with query parameters
    rv = client.get("/search?keywords=engineer&company=Tech&location=New+York")
    
    # Debug response if status is not 200
    if rv.status_code != 200:
        print(f"Response data: {rv.data.decode('utf-8')}")
    
    assert rv.status_code == 200
    
    # Parse and verify response
    data = json.loads(rv.data)
    assert len(data) == 1
    assert data[0] == {
        "title": "Software Engineer",
        "company": "Tech Corp",
        "location": "New York, NY",
        "type": "Full-time",
        "link": "https://www.careerbuilder.com/job/123",
        "externalId": "123",
    }


# Test 3: Application Data Retrieval
def test_get_data(client, user):
    user, header = user
    user.applications = []
    user.save()
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    assert json.loads(rv.data) == []

    application = {
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user.applications = [application]
    user.save()
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    assert json.loads(rv.data) == [application]


# Test 3: Application Data Retrieval
def test_get_data(client, user):
    user, header = user
    user.applications = []
    user.save()
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    assert json.loads(rv.data) == []

    application = {
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user.applications = [application]
    user.save()
    rv = client.get("/applications", headers=header)
    assert rv.status_code == 200
    assert json.loads(rv.data) == [application]


# Test 4: Application Creation
def test_add_application(client, mocker, user):
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.save()
    rv = client.post(
        "/applications",
        headers=header,
        json={
            "application": {
                "jobTitle": "fakeJob12345",
                "companyName": "fakeCompany",
                "date": str(datetime.date(2021, 9, 23)),
                "status": "1",
            }
        },
    )
    assert rv.status_code == 400


# Test 5: Application Update
def test_update_application(client, user):
    user, header = user
    application = {
        "id": 3,
        "jobTitle": "test_edit",
        "companyName": "test_edit",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user.applications = [application]
    user.save()
    new_application = {
        "id": 3,
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 22)),
    }
    rv = client.put(
        "/applications/3", json={"application": new_application}, headers=header
    )
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["jobTitle"]
    assert jdata == "fakeJob12345"


# Test 6: Application Deletion
def test_delete_application(client, user):
    user, header = user
    application = {
        "id": 3,
        "jobTitle": "fakeJob12345",
        "companyName": "fakeCompany",
        "date": str(datetime.date(2021, 9, 23)),
        "status": "1",
    }
    user.applications = [application]
    user.save()
    rv = client.delete("/applications/3", headers=header)
    jdata = json.loads(rv.data.decode("utf-8"))["jobTitle"]
    assert jdata == "fakeJob12345"


# Test 7: Server Status Code
def test_alive_status_code(client):
    rv = client.get("/")
    assert rv.status_code == 200


# Test 8: User Logout
def test_logout(client, user):
    user, header = user
    rv = client.post("/users/logout", headers=header)
    assert rv.status_code == 200


# Test 9: Resume Upload (Text File)
def test_resume(client, mocker, user):
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
    mocker.patch("models.get_new_user_id", return_value=-1)
    user, header = user
    user.applications = []
    user.resumes = []
    user.save()
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 400


# Test 12: Resume Upload (Non-PDF)
def test_resume_non_pdf(client, mocker, user):
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


# Test 30: Search with Valid Parameters
def test_search_route(client, mocker):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 31: Search with No Results
def test_search_route_no_results(client, mocker):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[]
    )
    rv = client.get("/search?keywords=nonexistent&company=Nonexistent&location=Nowhere")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) == 0

# Test 33: Recommendations with Valid Data
def test_get_recommendations_route(client, mocker, user):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["Python"], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 34: Recommendations with No Skills
def test_get_recommendations_route_no_skills(client, user):
    user, header = user
    user.profiles = [Profile(skills=[], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# Test 35: Recommendations with No Locations
def test_get_recommendations_route_no_locations(client, user):
    user, header = user
    user.profiles = [Profile(skills=[], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# Test 36: Recommendations with Multiple Job Levels
def test_get_recommendations_route_multiple_job_levels(client, mocker, user):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = user.profiles = [Profile(skills=["Python"], locations=["New York"], job_levels=["Entry-Level", "Director", "Intern"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 37: Search with Special Characters
def test_search_route_special_characters(client, mocker):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New+York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 38: Recommendations with Multiple Skills
def test_get_recommendations_route_multiple_skills(client, mocker, user):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["JavaScript", "Python", "Cooking"], locations=["New York"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 39: Recommendations with Multiple Locations
def test_get_recommendations_route_multiple_locations(client, mocker, user):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    user, header = user
    user.profiles = [Profile(skills=["Python"], locations=["New York", "San Fransisco", "Raleigh"])]
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 40: Search with Long Keywords
def test_search_route_long_keywords(client, mocker):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    long_keywords = "engineer" * 50
    rv = client.get(f"/search?keywords={long_keywords}&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# Test 41: Recommendations with Invalid User Data
def test_get_recommendations_route_no_user_data(client, mocker):
    mocker.patch(
        "routes.jobs.scrape_careerbuilder_jobs",
        return_value=[
            {
                "company": "Scale AI",
                "id": "J3R5G06ZWMK43M198Z2",
                "link": "https://www.careerbuilder.com/job/J3R5G06ZWMK43M198Z2",
                "location": "New York, NY (Onsite)",
                "title": "Mission Software Engineer, Federal",
                "type": "Full-Time"
            }
        ]
    )
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 500

# Test 41: Get Default Profile (No Profiles)
def test_get_profile_no_profiles(client, user):
    user, header = user
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 404
    assert json.loads(rv.data) == {"error": "No profile available"}


# Test 42: Get Default Profile
def test_get_default_profile(client, user):
    user, header = user
    user.email = "test@example.com"
    profile = Profile(profileName="Test Profile", skills=["Python"])
    user.profiles.append(profile)
    user.save()
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profileName"] == "Test Profile"
    assert data["skills"] == ["Python"]
    assert data["email"] == "test@example.com"
    assert data["profileid"] == 0


# Test 43: Get Profile by ID
def test_get_profile_by_id(client, user):
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    rv = client.get("/getProfile/1", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profileName"] == "Profile 2"
    assert data["profileid"] == 1


# Test 44: Get Profile with Invalid ID
def test_get_profile_invalid_id(client, user):
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    rv = client.get("/getProfile/999", headers=header)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 45: Update Default Profile
def test_update_default_profile(client, user):
    user, header = user
    profile = Profile(profileName="Initial Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"profileName": "Updated Profile", "skills": ["Java"]}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[0].profileName == "Updated Profile"
    assert updated_user.profiles[0].skills == ["Java"]


# Test 46: Update Profile by ID
def test_update_profile_by_id(client, user):
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    update_data = {"profileName": "Updated Profile 2"}
    rv = client.post("/updateProfile/1", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[1].profileName == "Updated Profile 2"


# Test 47: Update Profile with Invalid Field
def test_update_profile_invalid_field(client, user):
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"invalid_field": "value"}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid field: invalid_field"}


# Test 48: Update Profile with Invalid ID
def test_update_profile_invalid_id(client, user):
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"profileName": "Updated"}
    rv = client.post("/updateProfile/999", headers=header, json=update_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 49: Update Non-existent Default Profile
def test_update_create_default_profile(client, user):
    user, header = user
    update_data = {"profileName": "New Profile", "skills": ["Python"]}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert len(updated_user.profiles) == 1
    assert updated_user.profiles[0].profileName == "New Profile"


# Test 50: Create Profile
def test_create_profile(client, user):
    user, header = user
    profile_data = {"profileName": "New Profile", "skills": ["Java"]}
    rv = client.post("/createProfile", headers=header, json=profile_data)
    assert rv.status_code == 201
    data = json.loads(rv.data)
    assert data["message"] == "Profile created successfully"
    assert data["profileid"] == 0
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.profiles[0].profileName == "New Profile"


# Test 51: Create Profile with Invalid Field
def test_create_profile_invalid_field(client, user):
    user, header = user
    profile_data = {"invalid_field": "value"}
    rv = client.post("/createProfile", headers=header, json=profile_data)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid field: invalid_field"}


# Test 52: Set Default Profile
def test_set_default_profile(client, user):
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.save()
    rv = client.post("/setDefaultProfile/1", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["message"] == "Default profile updated successfully"
    assert data["default_profile"] == 1
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.default_profile == 1


# Test 53: Set Default Profile with Invalid ID
def test_set_default_profile_invalid_id(client, user):
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    rv = client.post("/setDefaultProfile/999", headers=header)
    assert rv.status_code == 400
    assert json.loads(rv.data) == {"error": "Invalid profile ID"}


# Test 54: Get Profile List (Empty)
def test_get_profile_list_empty(client, user):
    user, header = user
    rv = client.get("/getProfileList", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["profiles"] == []
    assert data["default_profile"] == 0


# Test 55: Get Profile List
def test_get_profile_list(client, user):
    user, header = user
    profile1 = Profile(profileName="Profile 1")
    profile2 = Profile(profileName="Profile 2")
    user.profiles.extend([profile1, profile2])
    user.default_profile = 1
    user.save()
    rv = client.get("/getProfileList", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data["profiles"]) == 2
    assert data["profiles"][0]["profileName"] == "Profile 1"
    assert data["profiles"][0]["isDefault"] == False
    assert data["profiles"][1]["profileName"] == "Profile 2"
    assert data["profiles"][1]["isDefault"] == True
    assert data["default_profile"] == 1


# Test 56: Update Profile with User Field
def test_update_profile_user_field(client, user):
    user, header = user
    profile = Profile(profileName="Test Profile")
    user.profiles.append(profile)
    user.save()
    update_data = {"email": "new@example.com"}
    rv = client.post("/updateProfile", headers=header, json=update_data)
    assert rv.status_code == 200
    updated_user = Users.objects(id=user.id).first()
    assert updated_user.email == "new@example.com"


# Test 57: Get Profile with Missing Header
def test_get_profile_missing_header(client):
    rv = client.get("/getProfile")
    assert rv.status_code == 500
    assert json.loads(rv.data) == {"error": "Internal server error"}


# Test 58: Create Multiple Profiles
def test_create_multiple_profiles(client, user):
    user, header = user
    profile_data1 = {"profileName": "Profile 1", "skills": ["Python"]}
    profile_data2 = {"profileName": "Profile 2", "skills": ["Java"]}
    rv1 = client.post("/createProfile", headers=header, json=profile_data1)
    rv2 = client.post("/createProfile", headers=header, json=profile_data2)
    assert rv1.status_code == 201
    assert rv2.status_code == 201
    data1 = json.loads(rv1.data)
    data2 = json.loads(rv2.data)
    assert data1["profileid"] == 0
    assert data2["profileid"] == 1
    updated_user = Users.objects(id=user.id).first()
    assert len(updated_user.profiles) == 2
    assert updated_user.profiles[0].profileName == "Profile 1"
    assert updated_user.profiles[1].profileName == "Profile 2"
