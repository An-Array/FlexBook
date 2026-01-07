import pytest
import httpx
import asyncio
from datetime import datetime, timedelta

# Configuration
BASE_URL = "http://127.0.0.1:8000"

async def create_test_user(email, password, client):
    """Create a test user if they don't exist"""
    user_payload = {
        "email": email,
        "password": password,
        "venues": []  # Empty venues list as per your schema
    }
    
    try:
        # Try to create the user via /signup endpoint
        response = await client.post(f"{BASE_URL}/signup", json=user_payload)
        if response.status_code == 201:
            print(f"✓ Created user: {email}")
        elif response.status_code == 409:
            # User already exists (your API returns 409 for conflicts)
            print(f"→ User {email} already exists")
        else:
            print(f"⚠ Unexpected response for {email}: {response.status_code} - {response.text}")
            response.raise_for_status()
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 409:
            print(f"→ User {email} already exists")
        else:
            print(f"❌ HTTP Error creating user {email}: {e.response.status_code} - {e.response.text}")
            raise
    except Exception as e:
        print(f"❌ Error creating user {email}: {e}")
        raise


async def setup_test_users(client, num_users):
    """Create multiple test users for concurrent testing"""
    user_creation_tasks = []
    
    for i in range(1, num_users+1):
        email = f"test_user_{i}@example.com"
        password = f"testpass123_{i}"
        task = create_test_user(email, password, client)
        user_creation_tasks.append(task)
    
    # Create all users concurrently
    await asyncio.gather(*user_creation_tasks)
    print(f"✓ User setup complete for {num_users} users")



@pytest.mark.asyncio
async def test_setup_only():
    """
    Just create users for manual testing
    """
    async with httpx.AsyncClient() as client:
        await setup_test_users(client, 50)  # Create 15 test users
        print("✓ All test users created successfully!")