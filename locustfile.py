from locust import HttpUser, task, between
import uuid

class BookingUser(HttpUser):
    wait_time = between(0.1, 0.5)
    token = None

    def on_start(self):
        email = f"user_{uuid.uuid4()}@test.com"
        password = "test1234"

        reg = self.client.post("/auth/register", json={
            "email": email,
            "password": password
        })

        if reg.status_code != 200:
            return

        login = self.client.post("/auth/login", data={
            "username": email,
            "password": password
        })

        if login.status_code != 200:
            return

        self.token = login.json().get("access_token")

    @task
    def book_seat(self):
        if not self.token:
            return
        self.client.post(
            "/bookings/",
            json={"seat_id": 1},
            headers={"Authorization": f"Bearer {self.token}"}
        )