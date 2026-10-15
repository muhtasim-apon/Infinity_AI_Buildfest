"""Locust alternative to k6 (Python). Run: locust -f tests/concurrency/locustfile.py --host <staging>.
Staging only. Not yet executed."""

from locust import HttpUser, between, task


class Farmer(HttpUser):
    wait_time = between(1, 3)

    def on_start(self) -> None:
        r = self.client.post("/v1/demo/session", json={"role": "user"})
        self.token = r.json().get("access_token", "") if r.ok else ""

    @task(3)
    def history(self) -> None:
        self.client.get("/v1/scans?limit=20", headers={"Authorization": f"Bearer {self.token}"})

    @task(1)
    def health(self) -> None:
        self.client.get("/healthz")
