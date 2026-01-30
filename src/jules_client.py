"""Base HTTP client for the Jules REST API."""

import os
import sys
from typing import Any, Generator, Optional

import requests
from dotenv import load_dotenv


class JulesAPIError(Exception):
    """Custom exception for Jules API errors."""

    def __init__(self, status_code: int, message: str, status: str = ""):
        self.status_code = status_code
        self.message = message
        self.status = status
        super().__init__(f"[{status_code}] {message}")


class JulesClient:
    """HTTP client for interacting with the Jules REST API."""

    BASE_URL = "https://jules.googleapis.com/v1alpha"

    def __init__(self):
        """Initialize the client with API key from environment."""
        load_dotenv()
        self.api_key = os.getenv("JULES_API_KEY")

        if not self.api_key:
            print("Error: JULES_API_KEY not found.", file=sys.stderr)
            print("Please set it in your .env file or environment.", file=sys.stderr)
            print("Get your API key from: https://jules.google.com/settings", file=sys.stderr)
            sys.exit(1)

        self.session = requests.Session()
        from . import __version__
        self.session.headers.update({
            "x-goog-api-key": self.api_key,
            "Content-Type": "application/json",
            "User-Agent": f"Jules-API-CLI/{__version__}",
        })

    def _handle_response(self, response: requests.Response) -> dict:
        """Handle API response and raise appropriate errors."""
        try:
            data = response.json() if response.text else {}
        except ValueError:
            data = {}

        if not response.ok:
            error = data.get("error", {})
            message = error.get("message", response.reason or "Unknown error")
            status = error.get("status", "")
            raise JulesAPIError(response.status_code, message, status)

        return data

    def get(self, endpoint: str, params: Optional[dict] = None) -> dict:
        """Make a GET request to the API."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.get(url, params=params)
        return self._handle_response(response)

    def post(self, endpoint: str, data: Optional[dict] = None) -> dict:
        """Make a POST request to the API."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.post(url, json=data or {})
        return self._handle_response(response)

    def delete(self, endpoint: str) -> dict:
        """Make a DELETE request to the API."""
        url = f"{self.BASE_URL}/{endpoint.lstrip('/')}"
        response = self.session.delete(url)
        return self._handle_response(response)

    def paginate(
        self,
        endpoint: str,
        params: Optional[dict] = None,
        page_size: int = 30,
        max_pages: Optional[int] = None,
    ) -> Generator[dict, None, None]:
        """
        Iterate through paginated results.

        Args:
            endpoint: API endpoint to call
            params: Additional query parameters
            page_size: Number of items per page
            max_pages: Maximum number of pages to fetch (None for all)

        Yields:
            Each item from the paginated results
        """
        params = params or {}
        params["pageSize"] = page_size
        page_count = 0

        while True:
            data = self.get(endpoint, params)

            # Yield items from the response
            # Try common list keys
            for key in ["sessions", "activities", "sources"]:
                if key in data:
                    yield from data[key]
                    break

            # Check for next page
            next_token = data.get("nextPageToken")
            if not next_token:
                break

            page_count += 1
            if max_pages and page_count >= max_pages:
                break

            params["pageToken"] = next_token


# Singleton instance
_client: Optional[JulesClient] = None


def get_client() -> JulesClient:
    """Get or create the singleton client instance."""
    global _client
    if _client is None:
        _client = JulesClient()
    return _client
