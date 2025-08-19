from locust import HttpUser, task, between
import random

# TO RUN:  locust -f tests/race_condition.py --host http://127.0.0.1:8000

USERS =  [
    (f"test_user_{i}@example.com", f"testpass123_{i}") for i in range(51)
]

VENUE_ID = 40

BOOKING_PAYLOAD = {
    "venue_id": VENUE_ID,
    "start_time": "2025-09-19T10:00:00Z",
    "end_time": "2025-09-19T11:00:00Z"
}


class BookingUser(HttpUser):
    wait_time = between(0,0) # how long a user waits between tasks

    def on_start(self):
        """
        Called when a simulated user starts.
        Logs in and stores the JWT token.
        """
        self.username, self.password = random.choice(USERS)  # pick a unique user for each locust instance

        response = self.client.post(
            "/login",  # adjust to your actual login route
            data={
                "username": self.username,
                "password": self.password
            }
        )

        if response.status_code == 200:
            token = response.json().get("access_token")
            self.client.headers.update({
                "Authorization": f"Bearer {token}"
            })
        else:
            print(f"Login failed for {self.username}: {response.text}")

    @task
    def try_booking(self):
        """
        All users try to book the same venue at overlapping times.
        This will reveal if your race condition handling works.
        """
        

        response = self.client.post("/bookings/", json=BOOKING_PAYLOAD)

        if response.status_code == 200:
            print(f"{self.username} booking succeeded")
        else:
            print(f"{self.username} booking failed: {response.text}")
