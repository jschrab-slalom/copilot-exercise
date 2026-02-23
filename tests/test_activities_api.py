from urllib.parse import quote


def test_get_activities_returns_expected_structure(client):
    response = client.get("/activities")

    assert response.status_code == 200
    payload = response.json()
    assert isinstance(payload, dict)
    assert "Chess Club" in payload

    for details in payload.values():
        assert "description" in details
        assert "schedule" in details
        assert "max_participants" in details
        assert "participants" in details
        assert isinstance(details["participants"], list)


def test_signup_adds_participant_successfully(client):
    activity_name = "Chess Club"
    email = "newstudent@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": email},
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Signed up {email} for {activity_name}"}

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email in participants


def test_signup_rejects_duplicate_participant(client):
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"

    response = client.post(
        f"/activities/{quote(activity_name)}/signup",
        params={"email": existing_email},
    )

    assert response.status_code == 400
    assert response.json() == {"detail": "Student is already signed up"}


def test_signup_unknown_activity_returns_404(client):
    response = client.post(
        f"/activities/{quote('Unknown Club')}/signup",
        params={"email": "student@mergington.edu"},
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_removes_participant_successfully(client):
    activity_name = "Chess Club"
    email = "michael@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(email)}"
    )

    assert response.status_code == 200
    assert response.json() == {"message": f"Unregistered {email} from {activity_name}"}

    activities_response = client.get("/activities")
    participants = activities_response.json()[activity_name]["participants"]
    assert email not in participants


def test_unregister_unknown_activity_returns_404(client):
    response = client.delete(
        f"/activities/{quote('Unknown Club')}/participants/{quote('student@mergington.edu')}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Activity not found"}


def test_unregister_missing_participant_returns_404(client):
    activity_name = "Chess Club"
    missing_email = "notenrolled@mergington.edu"

    response = client.delete(
        f"/activities/{quote(activity_name)}/participants/{quote(missing_email)}"
    )

    assert response.status_code == 404
    assert response.json() == {"detail": "Participant not found"}
