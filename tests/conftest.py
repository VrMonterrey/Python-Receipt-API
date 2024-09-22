import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)) + "/..")
from app.main import app
from app.database import Base, get_db
from app.config import settings
from fastapi.testclient import TestClient

SQLALCHEMY_DATABASE_URL = settings.DATABASE_URL_TEST
engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="module")
def client():
    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.pop(get_db, None)

@pytest.fixture(scope="module")
def access_token(client):
    response = client.post(
        "/users/register",
        json={
            "username": "testuser",
            "password": "testpass",
            "name": "Test",
            "surname": "User",
        },
    )
    assert response.status_code == 200

    response = client.post(
        "/users/login", data={"username": "testuser", "password": "testpass"}
    )
    assert response.status_code == 200
    return response.json()["access_token"]

@pytest.fixture(scope="session", autouse=True)
def flush_database():
    yield
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)