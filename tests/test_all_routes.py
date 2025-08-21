# TO RUN: pytest -v (in root - auto detects the file if starting or ending with {test_ / _test})
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import sys
import os
from datetime import datetime, timedelta, timezone

# Add the project root directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.main import app  # Make sure your main FastAPI app instance is named 'app'
from app.db import Base, get_db, settings
from app.db import models

# Constants to by-pass Constraints Checking of Pydantic validators
now = datetime.now(timezone.utc)
minute = 0 if now.minute < 30 else 30


# --- Test Database Setup ---
# Use a separate database for testing (e.g., flexbook_test)
SQLALCHEMY_DATABASE_URL = f"postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}_test"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# This fixture will be run for each test function
@pytest.fixture(scope="function")
def session():
    """
    Fixture to create a fresh, clean database for each test function.
    This ensures tests are isolated and don't interfere with each other.
    """
    Base.metadata.drop_all(bind=engine)  # Drop all tables
    Base.metadata.create_all(bind=engine)  # Create all tables
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

@pytest.fixture(scope="function")
def client(session):
    """
    Fixture to create a TestClient that uses the isolated test database.
    """
    def override_get_db():
        try:
            yield session
        finally:
            session.close()
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)

# --- Test Data and Authentication ---

@pytest.fixture
def test_users(client, session): 
    """
    Fixture to create a set of users with different roles.
    Directly manipulates the DB to set roles, as the signup endpoint doesn't allow it.
    """
    users_data = [
        {"email": "admin@example.com", "password": "password123", "role": "admin"},
        {"email": "owner@example.com", "password": "password123", "role": "owner"},
        {"email": "user@example.com", "password": "password123", "role": "user"}
    ]
    
    created_users = []
    for user_data in users_data:
        # Create user via signup to get hashed password
        res = client.post("/signup", json={"email": user_data["email"], "password": user_data["password"]})
        new_user = res.json()
        
        # Manually update the role in the test database
        user_in_db = session.query(models.User).filter(models.User.id == new_user['id']).first()
        if user_in_db:
            user_in_db.role = user_data["role"]
            session.commit()
            session.refresh(user_in_db)
        created_users.append(new_user)
        
    return created_users


def get_token(email, password, client):
    """Helper function to log in and retrieve a JWT token."""
    login_data = {
        "username": email,
        "password": password
    }
    res = client.post("/login", data=login_data)
    assert res.status_code == 200, f"Login failed for {email}: {res.text}"
    token = res.json()["access_token"]
    return token

# --- USER ROUTE TESTS ---

def test_signup(client):
    res = client.post("/signup", json={"email": "testsignup@example.com", "password": "password123"})
    assert res.status_code == 201
    assert res.json()["email"] == "testsignup@example.com"

def test_login(client, test_users):
    token = get_token("user@example.com", "password123", client)
    assert token is not None

def test_get_all_users_as_admin(client, test_users):
    admin_token = get_token("admin@example.com", "password123", client)
    res = client.get("/users", headers={"Authorization": f"Bearer {admin_token}"})
    assert res.status_code == 200
    assert len(res.json()) == 3

def test_get_all_users_as_non_admin(client, test_users):
    user_token = get_token("user@example.com", "password123", client)
    res = client.get("/users", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403 # Forbidden

# --- VENUE ROUTE TESTS ---

def test_create_venue_as_owner(client, test_users):
    owner_token = get_token("owner@example.com", "password123", client)
    res = client.post("/venues", json={"name": "My Awesome Venue"}, headers={"Authorization": f"Bearer {owner_token}"})
    assert res.status_code == 201
    assert res.json()["name"] == "My Awesome Venue"

def test_create_venue_as_user(client, test_users):
    user_token = get_token("user@example.com", "password123", client)
    res = client.post("/venues", json={"name": "This Should Fail"}, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 403 # Forbidden

def test_get_all_venues(client, test_users):
    user_token = get_token("user@example.com", "password123", client)
    res = client.get("/venues", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200

# --- BOOKING ROUTE TESTS ---

@pytest.fixture
def test_venue(client, test_users):
    """Fixture to create a venue for booking tests."""
    owner_token = get_token("owner@example.com", "password123", client)
    res = client.post("/venues", json={"name": "Test Booking Venue"}, headers={"Authorization": f"Bearer {owner_token}"})
    assert res.status_code == 201
    return res.json()

def test_create_booking(client, test_users, test_venue):
    user_token = get_token("user@example.com", "password123", client)
    start_time = (now.replace(minute=minute, second=0, microsecond=0) + timedelta(days=1)).isoformat()
    end_time = (datetime.fromisoformat(start_time) + timedelta(days=1, hours=1)).isoformat()

    booking_data = {
        "venue_id": test_venue["id"],
        "start_time": start_time,
        "end_time": end_time
    }
    res = client.post("/bookings/", json=booking_data, headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 201
    assert res.json()["venue_id"] == test_venue["id"]

def test_booking_conflict(client, test_users, test_venue):
    user_token = get_token("user@example.com", "password123", client)
    start_time = (now.replace(minute=minute, second=0, microsecond=0) + timedelta(days=2)).isoformat()
    end_time = (datetime.fromisoformat(start_time) + timedelta(hours=2)).isoformat()

    # First booking
    res1 = client.post("/bookings/", json={"venue_id": test_venue["id"], "start_time": start_time, "end_time": end_time}, headers={"Authorization": f"Bearer {user_token}"})
    assert res1.status_code == 201

    # Conflicting booking
    conflict_start = (now.replace(minute=minute, second=0, microsecond=0) + timedelta(days=2, hours=1)).isoformat()
    conflict_end = (datetime.fromisoformat(start_time) + timedelta(hours=3)).isoformat()
    res2 = client.post("/bookings/", json={"venue_id": test_venue["id"], "start_time": conflict_start, "end_time": conflict_end}, headers={"Authorization": f"Bearer {user_token}"})
    assert res2.status_code == 409 # Conflict

def test_get_own_booking_details(client, test_users, test_venue):
    user_token = get_token("user@example.com", "password123", client)
    start_time = (now.replace(minute=minute, second=0, microsecond=0) + timedelta(days=3)).isoformat()
    end_time = (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat()
    booking_res = client.post("/bookings/", json={"venue_id": test_venue["id"], "start_time": start_time, "end_time": end_time}, headers={"Authorization": f"Bearer {user_token}"})
    assert booking_res.status_code == 201
    booking_id = booking_res.json()["id"]

    res = client.get(f"/bookings/{booking_id}", headers={"Authorization": f"Bearer {user_token}"})
    assert res.status_code == 200
    assert res.json()["id"] == booking_id

def test_get_others_booking_details_as_user(client, test_users, test_venue):
    user_token = get_token("user@example.com", "password123", client)
    owner_token = get_token("owner@example.com", "password123", client)

    start_time = (now.replace(minute=minute, second=0, microsecond=0) + timedelta(days=4)).isoformat()
    end_time = (datetime.fromisoformat(start_time) + timedelta(hours=1)).isoformat()
    booking_res = client.post("/bookings/", json={"venue_id": test_venue["id"], "start_time": start_time, "end_time": end_time}, headers={"Authorization": f"Bearer {user_token}"})
    assert booking_res.status_code == 201
    booking_id = booking_res.json()["id"]

    # Owner tries to get user's booking
    res = client.get(f"/bookings/{booking_id}", headers={"Authorization": f"Bearer {owner_token}"})
    assert res.status_code == 401 # Unauthorized
