import pytest
import requests
import time
import subprocess
from http import HTTPStatus


def start_server():
    process = subprocess.Popen(["python", "tus_storagehandler"])
    time.sleep(5)  # Give the server time to start
    return process


def stop_server(process):
    process.terminate()


@pytest.fixture
def base_url():
    """Return the base URL for the service."""
    return "http://localhost:8080"


def test_get_root(base_url):
    """Test the root endpoint of the service."""
    response = requests.get(f"{base_url}/elixircoud/csh/v1")

    assert (
        response.status_code == HTTPStatus.OK
    ), f"Expected status code 200, got {response.status_code}"
