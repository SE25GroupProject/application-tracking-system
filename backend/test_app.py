"""
Test module for the backend
"""

import hashlib
from io import BytesIO

import json
import datetime
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
