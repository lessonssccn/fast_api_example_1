import os

TEST_DB_FILE = "./test.db"
SQLITE_DATABASE_URL_TEST = f"sqlite:///{TEST_DB_FILE}"
os.environ['TESTING'] = 'True'
os.environ['SQLITE_TEST'] = SQLITE_DATABASE_URL_TEST

from fastapi.testclient import TestClient
from app.db.database import engine, Base
from app.main import app
import pytest

new_user = {"name":"user_1", "password":"psw_1"}
update_user = {"name":"new_name", "password":"new_psw"}

@pytest.fixture()
def temp_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine) 

@pytest.fixture()
def add_user():
    with TestClient(app) as client:
        response = client.post("/api/users/", json=new_user)

def test_root():
    with TestClient(app) as client:
        response = client.get("/")
    assert response.status_code == 200


def test_add_user(temp_db):
    with TestClient(app) as client:
        response = client.post("/api/users/", json=new_user)
    assert response.status_code == 201
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == new_user["name"]

def test_get_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.get("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == new_user["name"]

def test_get_user_with_error_id(temp_db):
    with TestClient(app) as client:
        response = client.get("/api/users/2")
    assert response.status_code == 404

def test_delete_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.delete("/api/users/1")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True

def test_update_user(temp_db, add_user):
    with TestClient(app) as client:
        response = client.put("/api/users/1", json=update_user)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] == True
    assert data["data"]["id"] == 1
    assert data["data"]["name"] == update_user["name"]
