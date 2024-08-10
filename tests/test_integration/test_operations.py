"""Test operations for the tus-storagehandler service."""

from http import HTTPStatus
from unittest import mock

import requests


def test_get_root():
    """Test the root endpoint of the service with mocked response."""
    with mock.patch("requests.get") as mock_get:
        response = requests.get("http://localhost:8080/elixircoud/csh/v1")
        
        assert response.status_code == HTTPStatus.OK, (
            f"Expected status code 200, got {response.status_code}"
        )
        mock_get.assert_called_once_with("http://localhost:8080/elixircoud/csh/v1")