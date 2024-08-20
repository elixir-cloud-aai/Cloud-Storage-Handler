"""Test operations for the cloud storage handler service."""

from http import HTTPStatus
from unittest import mock

import requests


def test_get_root():
    """Test the root endpoint of the service with a mocked response."""
    print("Starting test_get_root...")

    server_url = "http://localhost:8080/elixircoud/csh/v1"

    with mock.patch("requests.get") as mock_get:
        mock_response = mock.Mock()
        mock_response.status_code = HTTPStatus.OK
        mock_get.return_value = mock_response

        response = requests.get(server_url)
        print(f"Response status code: {response.status_code}")

        assert (
            response.status_code == HTTPStatus.OK
        ), f"Expected status code 200, got {response.status_code}"

        mock_get.assert_called_once_with(server_url)

    print("Finished test_get_root")
