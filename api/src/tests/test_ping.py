# For each route:
# 1. write a test
# 2. run the test, to ensure it fails (red)
# 3. write just enough code to get the test to pass (green)
# 4. refactor (if necessary)
from starlette.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_hello():
    response = client.get("/ping")
    assert response.status_code == 200
    assert response.json() == {"ping":"pong"}