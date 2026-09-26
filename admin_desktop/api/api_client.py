"""
API CLIENT BOUNDARY (Stage 2 placeholder)
==========================================
This is the single centralized place that will eventually own all HTTP
communication with the FastAPI backend. No Tkinter UI code should ever
import `requests`/`httpx` directly, and no API URLs should be scattered
outside this file.

Stage 1: this class is NOT used by the running application. The service
layer (see services/) talks to mock/ modules instead. It exists now so the
integration boundary is explicit and so services can be swapped from
MockXService to ApiXService later without touching the UI.

Stage 2: services will construct requests through this client, which will
own:
    * base URL configuration
    * default headers / auth token attachment
    * timeout handling
    * centralized error handling & response parsing
    * retry policy (if any)
"""

from config.settings import API_BASE_URL, API_TIMEOUT_SECONDS


class ApiClientError(Exception):
    """Raised for any failed API call once real networking is implemented."""


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT_SECONDS):
        self.base_url = base_url
        self.timeout = timeout
        self._auth_token: str | None = None

    def set_auth_token(self, token: str) -> None:
        self._auth_token = token

    def clear_auth_token(self) -> None:
        self._auth_token = None

    # ------------------------------------------------------------------
    # The methods below are intentionally unimplemented in Stage 1.
    # Stage 2 will implement them using `requests`/`httpx`, attaching
    # `Authorization: Bearer <token>` headers from self._auth_token, and
    # raising ApiClientError on non-2xx responses.
    # ------------------------------------------------------------------

    def get(self, path: str, params: dict | None = None):
        raise NotImplementedError(
            "ApiClient.get() is a Stage 2 integration point. "
            f"Would call: GET {self.base_url}{path}"
        )

    def post(self, path: str, payload: dict | None = None):
        raise NotImplementedError(
            "ApiClient.post() is a Stage 2 integration point. "
            f"Would call: POST {self.base_url}{path}"
        )

    def put(self, path: str, payload: dict | None = None):
        raise NotImplementedError(
            "ApiClient.put() is a Stage 2 integration point. "
            f"Would call: PUT {self.base_url}{path}"
        )

    def delete(self, path: str):
        raise NotImplementedError(
            "ApiClient.delete() is a Stage 2 integration point. "
            f"Would call: DELETE {self.base_url}{path}"
        )


# Single shared instance the service layer will import in Stage 2, e.g.:
#   from api.api_client import api_client
api_client = ApiClient()
