def test_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser2",
            "password": "testpass2",
            "name": "Test2",
            "surname": "User2",
        },
    )
    assert response.status_code == 200
    assert response.json()["username"] == "testuser2"
    assert response.json()["name"] == "Test2"
    assert response.json()["surname"] == "User2"


def test_login_user(client):
    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
    assert "refresh_token" in response.json()


def test_invalid_register_user(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "name": "Test",
            "surname": "User",
        },
    )
    assert response.status_code == 422


def test_invalid_login(client):
    response = client.post(
        "/users/login", data={"username": "wronguser", "password": "wrongpass"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Incorrect username or password"