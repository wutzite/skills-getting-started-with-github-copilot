from urllib.parse import quote

from fastapi.testclient import TestClient

from src.app import app


client = TestClient(app)


def test_unregister_participant_removes_user_from_activity():
    email = "delete-check-1@mergington.edu"

    signup_response = client.post(
        f"/activities/Chess Club/signup?email={quote(email)}"
    )
    assert signup_response.status_code == 200

    unregister_response = client.delete(
        f"/activities/Chess Club/participants/{quote(email)}"
    )

    assert unregister_response.status_code == 200
    assert unregister_response.json()["message"] == (
        f"Unregistered {email} from Chess Club"
    )

    activities_response = client.get("/activities")
    activities = activities_response.json()
    assert email not in activities["Chess Club"]["participants"]


def test_unregister_participant_returns_error_when_not_registered():
    email = "delete-check-2@mergington.edu"

    response = client.delete(
        f"/activities/Chess Club/participants/{quote(email)}"
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Student is not signed up for this activity"
