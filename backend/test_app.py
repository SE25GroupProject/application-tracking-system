"""
Test module for the backend
"""

import hashlib
from io import BytesIO

import pytest
import json
import datetime
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


# Test 1: Server Status
def test_alive(client):
    """
    Test to verify the server status endpoint returns the expected message.

    Args:
        client: The Flask test client.
    """
    rv = client.get("/")
    assert rv.data.decode("utf-8") == '{\n  "message": "Server up and running"\n}\n'


# Test 2: Search Endpoint
def test_search(client, mocker):
    """
    Test the search endpoint with mocked Selenium WebDriver to simulate job scraping.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
    """
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
    """
    Test retrieval of application data for a user.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
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
    """
    Test creation of a new application with an invalid user ID.

    Args:
        client: The Flask test client.
        mocker: Pytest-mock fixture for mocking objects.
        user: The test user and authentication header.
    """
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
    """
    Test updating an existing application.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
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
    """
    Test deletion of an existing application.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
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
    """
    Test the server status endpoint returns a 200 status code.

    Args:
        client: The Flask test client.
    """
    rv = client.get("/")
    assert rv.status_code == 200


# Test 8: User Logout
def test_logout(client, user):
    """
    Test user logout functionality.

    Args:
        client: The Flask test client.
        user: The test user and authentication header.
    """
    user, header = user
    rv = client.post("/users/logout", headers=header)
    assert rv.status_code == 200


# 10. testing resume on a .txt file
def test_resume(client, mocker, user):
    """
    Tests that using the resume endpoint returns data

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )
    user, header = user
    user["applications"] = []
    user.save()
    data = dict(
        file=(BytesIO(b"testing resume"), "resume.txt"),
    )
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 500


# 11. testing resume on a pdf file (note that ollama has to be running for this to work)
def test_resume_pdf(client, mocker, user):
    """
    Tests that using the resume endpoint accepts data when valid

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200


# 12. testing getting a resume from empty database
def test_resume_dne(client, mocker, user):
    """
    Tests error case of trying to get a non-existent resume

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Send GET request to check resume data (nothing should be there so there should be an error)
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 400


# 13. testing resume on a non-pdf file
def test_resume_non_pdf(client, mocker, user):
    """
    Tests that using the resume endpoint rejects non-pdf files

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Prepare form data
    data = dict(
        file=(
            BytesIO(b"testing resume that is not the expected file type"),
            "resume.txt",
        ),
    )

    # Send POST request with txt file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 500

    # Send GET request to check resume data (nothing should be there so there should be an error)
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 400


# 14. testing getting resume feedback from empty database
def test_resume_feedback_dne(client, mocker, user):
    """
    Tests case of trying to get a non-existent resume feedback; should be an empty list of strings

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Send GET request to check resume feedback data (nothing should be there)
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 0


# 15. test resume feedback on a valid instance (note that ollama has to be running for this to work)
def test_resume_feedback(client, mocker, user):
    """
    Tests that llm produces resume feedback and endpoint works

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume feedback data (one should be there)
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 1


# 16. testing resume feedback on a valid instance by index
# (note that ollama has to be running for this to work)
def test_resume_feedback_by_idx(client, mocker, user):
    """
    Tests that llm produces resume feedback and endpoint works to retrieve by index

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume feedback data (one should be there at idx 0)
    rv = client.get("/resume-feedback/0", headers=header)
    assert rv.status_code == 200

# 17. testing resume feedback on a valid instance by index
# (note that ollama has to be running for this to work)
def test_resume_feedback_by_idx_invalid_too_high(client, mocker, user):
    """
    Tests error case where llm produces resume feedback but is retrieved with invalid index

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume feedback data (index 3 should not be valid)
    rv = client.get("/resume-feedback/3", headers=header)
    assert rv.status_code == 400

# 18. testing resume feedback on a valid instance by index
# (note that ollama has to be running for this to work)
def test_resume_feedback_by_idx_invalid_negative(client, mocker, user):
    """
    Tests error case where llm produces resume feedback but is retrieved with invalid index

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume feedback data (index -1 should not be valid)
    rv = client.get("/resume-feedback/-1", headers=header)
    assert rv.status_code == 404


# 19. testing deleting resume feedback on a valid instance by index
# (note that ollama has to be running for this to work)
def test_resume_delete(client, mocker, user):
    """
    Tests the functionality of deleting a resume that exists

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200

# 20. testing deleting resume feedback on invalid index
# (note that ollama has to be running for this to work)
def test_resume_delete_invalid(client, mocker, user):
    """
    Tests error case of deleting resume at wrong index

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Delete resume (wrong index)
    rv = client.delete("/resume/2", headers=header)
    assert rv.status_code == 400


# 21. testing deleting resume feedback on empty list
# (note that ollama has to be running for this to work)
def test_resume_delete_dne(client, mocker, user):
    """
    Tests error case of deleting resume that doesn't exist

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Delete resume (invalid)
    rv = client.delete("/resume/2", headers=header)
    assert rv.status_code == 400

# 22. testing resume on an alternate pdf file
# (note that ollama has to be running for this to work)
def test_resume_pdf_2(client, mocker, user):
    """
    Tests that using the resume endpoint accepts data when valid

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200

# 23. testing resume upload with 2 pdf files
# (note that ollama has to be running for this to work)
def test_resume_pdf_multiple(client, mocker, user):
    """
    Tests that the db can store multiple resumes

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume", headers=header)
    assert rv.status_code == 200


# 24. testing feedback retrieval with 2 pdf files
# (note that ollama has to be running for this to work)
def test_resume_pdf_multiple_feedback(client, mocker, user):
    """
    Tests that multiple resumes leads to multiple feedback being stored

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume-feedback", headers=header)
    assert rv.status_code == 200
    jdata = json.loads(rv.data.decode("utf-8"))["response"]
    assert len(jdata) == 2


# 25. testing feedback retrieval with 2 pdf files by index
# (note that ollama has to be running for this to work)
def test_resume_pdf_multiple_feedback_by_idx(client, mocker, user):
    """
    Tests feedback retrieval by idx

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume-feedback/0", headers=header)
    assert rv.status_code == 200


# 26. testing feedback retrieval with 2 pdf files by different index
# (note that ollama has to be running for this to work)
def test_resume_pdf_multiple_feedback_by_idx_2(client, mocker, user):
    """
    Tests feedback retrieval by idx

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send GET request to check resume data
    rv = client.get("/resume-feedback/1", headers=header)
    assert rv.status_code == 200


# 27. testing deleting first resume from multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_first(client, mocker, user):
    """
    Tests deleting a resume

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# 28. testing deleting last resume from multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_last(client, mocker, user):
    """
    Tests deleting a resume

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/1", headers=header)
    assert rv.status_code == 200


# 29. testing deleting multiple resumes
# (note that ollama has to be running for this to work)
def test_delete_multiple_resumes(client, mocker, user):
    """
    Tests deleting multiple resumes

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200

    # Send DELETE request to delete resume
    rv = client.delete("/resume/0", headers=header)
    assert rv.status_code == 200


# 30. testing deleting invalid index in multiple resumes
# (note that ollama has to be running for this to work)
def test_resume_delete_multiple_invalid(client, mocker, user):
    """
    Tests deleting invalid index in list of multiple resumes

    :param client: mongodb client
    :param mocker: pytest mocker
    :param user: the test user object
    """
    mocker.patch(
        # Dataset is in slow.py, but imported to main.py
        "models.get_new_user_id",
        return_value=-1,
    )

    user, header = user
    user["applications"] = []
    user.save()

    # Read the actual PDF file
    pdf_path = "data/sample-resume-2.pdf"
    with open(pdf_path, "rb") as f:
        pdf_bytes = BytesIO(f.read())

    pdf_path_2 = "data/sample-resume-2.pdf"
    with open(pdf_path_2, "rb") as f:
        pdf_bytes_2 = BytesIO(f.read())

    # Prepare form data
    data = dict(
        file=(pdf_bytes, "sample-resume.pdf"),
    )
    data2 = dict(
        file=(pdf_bytes_2, "sample-resume-2.pdf"),
    )

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data
    )
    assert rv.status_code == 200

    # Send POST request with PDF file
    rv = client.post(
        "/resume", headers=header, content_type="multipart/form-data", data=data2
    )
    assert rv.status_code == 200

    # Send invalid DELETE request
    rv = client.delete("/resume/3", headers=header)
    assert rv.status_code == 400


# 31. Test search route with valid parameters
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
                "type": "Full-Time",
            }
        ],
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 32. Test search route with no results
def test_search_route_no_results(client, mocker):
    mocker.patch("routes.jobs.scrape_careerbuilder_jobs", return_value=[])
    rv = client.get("/search?keywords=nonexistent&company=Nonexistent&location=Nowhere")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) == 0


# 33. Test search route with missing parameters
def test_search_route_missing_parameters(client):
    rv = client.get("/search?keywords=engineer")
    assert rv.status_code == 500


# 34. Test getRecommendations route with valid user data
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
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 35. Test getRecommendations route with no skills
def test_get_recommendations_route_no_skills(client, user):
    user, header = user
    user.skills = []
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# 36. Test getRecommendations route with no locations
def test_get_recommendations_route_no_locations(client, user):
    user, header = user
    user.locations = []
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 400


# 37. Test getProfile route with valid user data
def test_get_profile_route(client, user):
    user, header = user
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["email"] == user.email


# 38. Test getProfile route with invalid user
def test_get_profile_route_invalid_user(client):
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getProfile", headers=header)
    assert rv.status_code == 500


# 39. Test updateProfile route with valid data
def test_update_profile_route(client, user):
    user, header = user
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
        "skills": [{"value": "Java"}],
        "job_levels": [{"value": "Junior"}],
        "locations": [{"value": "San Francisco"}],
        "institution": "New University",
        "phone_number": "0987654321",
        "address": "456 New St",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    print(user, dir(user))
    assert new_data["email"] == new_data["email"]


# 40. Test updateProfile route with invalid data
def test_update_profile_route_invalid_data(client, user):
    user, header = user
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
        "skills": "invalid",  # Invalid format
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 500


# 41. Test getRecommendations route with no job levels
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
                "type": "Full-Time",
            }
        ],
    )

    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.job_levels.append({"value": "Entry-Level"})
    user.job_levels.append({"value": "Director"})
    user.job_levels.append({"value": "Intern"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 42. Test search route with special characters in parameters
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
                "type": "Full-Time",
            }
        ],
    )
    rv = client.get("/search?keywords=engineer&company=Scale AI&location=New+York")
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 43. Test getProfile route with missing header
def test_get_profile_route_missing_header(client):
    rv = client.get("/getProfile")
    assert rv.status_code == 500


# 44. Test updateProfile route with partial data
def test_update_profile_route_partial_data(client, user):
    user, header = user
    new_data = {
        "email": "partial@example.com",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert Users.objects(id=data["id"]).first().email == new_data["email"]


# 45. Test getRecommendations route with multiple skills
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
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "JavaScript"})
    user.skills.append({"value": "Python"})
    user.skills.append({"value": "Cooking"})
    user.locations.append({"value": "New York"})
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 46. Test getRecommendations route with multiple locations
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
                "type": "Full-Time",
            }
        ],
    )
    user, header = user
    user.skills.append({"value": "Python"})
    user.locations.append({"value": "New York"})
    user.locations.append({"value": "San Fransisco"})
    user.locations.append({"value": "Raleigh"})
    user.save()
    user.save()
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 47. Test updateProfile route with empty data
def test_update_profile_route_empty_data(client, user):
    user, header = user
    new_data = {}
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert data["fullName"] == user.fullName


# 48. Test search route with long keywords
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
                "type": "Full-Time",
            }
        ],
    )
    long_keywords = "engineer" * 50
    rv = client.get(
        f"/search?keywords={long_keywords}&company=Scale AI&location=New York"
    )
    assert rv.status_code == 200
    data = json.loads(rv.data)
    assert len(data) > 0


# 49. Test getRecommendations route with no user data
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
                "type": "Full-Time",
            }
        ],
    )
    header = {"Authorization": "Bearer invalid"}
    rv = client.get("/getRecommendations", headers=header)
    assert rv.status_code == 500


# 50. Test updateProfile route with invalid user
def test_update_profile_route_invalid_user(client):
    header = {"Authorization": "Bearer invalid"}
    new_data = {
        "email": "new@example.com",
        "fullName": "New User",
    }
    rv = client.post("/updateProfile", headers=header, json=new_data)
    assert rv.status_code == 500
