"""
Test module for the backend
"""

import hashlib

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
