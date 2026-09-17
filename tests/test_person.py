from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.main import app
from app.db import get_db
from app.models import Base


TEST_DATABASE_URL = "postgresql://program:test@localhost:5432/persons_test"

test_engine = create_engine(TEST_DATABASE_URL)

TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine
)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def setup_function():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)


def test_create_person():
    response = client.post(
        "/api/v1/persons",
        json={
            "name": "Ivan Ivanov",
            "age": 25,
            "address": "Moscow",
            "work": "Developer"
        }
    )

    assert response.status_code == 201
    assert response.text == ""
    assert response.headers["Location"].startswith("/api/v1/persons/")


def test_get_person():
    create_response = client.post(
        "/api/v1/persons",
        json={
            "name": "Ivan Ivanov",
            "age": 25,
            "address": "Moscow",
            "work": "Developer"
        }
    )

    person_id = int(
        create_response.headers["Location"].split("/")[-1]
    )

    response = client.get(f"/api/v1/persons/{person_id}")

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == person_id
    assert data["name"] == "Ivan Ivanov"
    assert data["age"] == 25
    assert data["address"] == "Moscow"
    assert data["work"] == "Developer"


def test_get_person_not_found():
    response = client.get("/api/v1/persons/99999")

    assert response.status_code == 404


def test_update_person():
    create_response = client.post(
        "/api/v1/persons",
        json={
            "name": "Ivan Ivanov",
            "age": 25,
            "address": "Moscow",
            "work": "Developer"
        }
    )

    person_id = int(
        create_response.headers["Location"].split("/")[-1]
    )

    response = client.patch(
        f"/api/v1/persons/{person_id}",
        json={
            "name": "Petr Petrov",
            "age": 30,
            "address": "Saint Petersburg",
            "work": "Engineer"
        }
    )

    assert response.status_code == 200

    data = response.json()

    assert data["name"] == "Petr Petrov"
    assert data["age"] == 30
    assert data["address"] == "Saint Petersburg"
    assert data["work"] == "Engineer"


def test_delete_person():
    create_response = client.post(
        "/api/v1/persons",
        json={
            "name": "Ivan Ivanov",
            "age": 25,
            "address": "Moscow",
            "work": "Developer"
        }
    )

    person_id = int(
        create_response.headers["Location"].split("/")[-1]
    )

    response = client.delete(
        f"/api/v1/persons/{person_id}"
    )

    assert response.status_code == 204
    assert response.text == ""

    get_response = client.get(
        f"/api/v1/persons/{person_id}"
    )

    assert get_response.status_code == 404