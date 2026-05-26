from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app

client = TestClient(app)


def test_root_redirects_to_static_index():
    # Arrange
    expected_location = "/static/index.html"

    # Act
    response = client.get("/", follow_redirects=False)

    # Assert
    assert response.status_code == 307
    assert response.headers["location"] == expected_location


def test_get_activities_returns_activity_list():
    # Arrange
    expected_keys = {"Chess Club", "Programming Class", "Gym Class"}

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_keys.issubset(set(data.keys()))


def test_signup_for_activity_adds_participant():
    # Arrange
    activity_name = "Chess Club"
    email = "aaa-signup@mergington.edu"
    encoded_email = quote(email)

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities")
    assert email in activities_response.json()[activity_name]["participants"]


def test_signup_for_activity_returns_error_when_duplicate():
    # Arrange
    activity_name = "Chess Club"
    email = "duplicate-signup@mergington.edu"
    encoded_email = quote(email)

    client.post(f"/activities/{quote(activity_name)}/signup?email={encoded_email}")

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student already signed up for this activity"


def test_signup_for_missing_activity_returns_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "missing-activity@mergington.edu"
    encoded_email = quote(email)

    # Act
    response = client.post(f"/activities/{quote(activity_name)}/signup?email={encoded_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"


def test_unregister_participant_removes_user_from_activity():
    # Arrange
    activity_name = "Chess Club"
    email = "backend-unregister@mergington.edu"
    encoded_email = quote(email)

    client.post(f"/activities/{quote(activity_name)}/signup?email={encoded_email}")

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{encoded_email}")

    # Assert
    assert response.status_code == 200
    assert response.json()["message"] == f"Unregistered {email} from {activity_name}"

    activities_response = client.get("/activities")
    assert email not in activities_response.json()[activity_name]["participants"]


def test_unregister_participant_returns_error_when_not_registered():
    # Arrange
    activity_name = "Chess Club"
    email = "not-registered@mergington.edu"
    encoded_email = quote(email)

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{encoded_email}")

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"


def test_unregister_missing_activity_returns_not_found():
    # Arrange
    activity_name = "Nonexistent Club"
    email = "missing-unregister@mergington.edu"
    encoded_email = quote(email)

    # Act
    response = client.delete(f"/activities/{quote(activity_name)}/participants/{encoded_email}")

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == "Activity not found"
