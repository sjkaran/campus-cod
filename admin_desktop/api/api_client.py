"""
API CLIENT — Stage 2 (live backend)
====================================
Single centralized place that owns all HTTP communication with the FastAPI
backend. No other module should construct a URL or open a socket — the
service layer (see services/) is the only thing that calls into this file.

Built on Python's standard library (urllib) rather than `requests`, so the
Admin desktop app still needs zero third-party packages.

Backend conventions this client understands:
  * Auth:          Authorization: Bearer <token>, obtained from POST /auth/login
  * Single item:   {"data": {...}}
  * Collection:    {"data": [...], "pagination": {"page","page_size","total"}}
  * Error:         {"detail": "..."}  with a non-2xx HTTP status
"""

import json
import urllib.request
import urllib.parse
import urllib.error

from config.settings import API_BASE_URL, API_TIMEOUT_SECONDS


class ApiClientError(Exception):
    """Raised for any failed API call. `status_code` is None for network-level
    failures (backend unreachable), or the HTTP status code otherwise."""

    def __init__(self, message: str, status_code: int | None = None):
        super().__init__(message)
        self.status_code = status_code


class ApiClient:
    def __init__(self, base_url: str = API_BASE_URL, timeout: int = API_TIMEOUT_SECONDS):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._auth_token: str | None = None

    def set_auth_token(self, token: str) -> None:
        self._auth_token = token

    def clear_auth_token(self) -> None:
        self._auth_token = None

    def _headers(self) -> dict:
        headers = {"Content-Type": "application/json", "Accept": "application/json"}
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"
        return headers

    def _build_url(self, path: str, params: dict | None) -> str:
        url = self.base_url + path
        if params:
            clean = {k: v for k, v in params.items() if v is not None and v != ""}
            if clean:
                url += "?" + urllib.parse.urlencode(clean)
        return url

    def _request(self, method: str, path: str, params: dict = None, json_body: dict = None,
                 raw: bool = False):
        url = self._build_url(path, params)
        data = json.dumps(json_body).encode("utf-8") if json_body is not None else None
        request = urllib.request.Request(url, data=data, method=method, headers=self._headers())
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                body = response.read()
                if raw:
                    return body
                text = body.decode("utf-8")
                return json.loads(text) if text else {}
        except urllib.error.HTTPError as e:
            body_text = e.read().decode("utf-8", errors="replace")
            try:
                detail = json.loads(body_text).get("detail", body_text)
            except (json.JSONDecodeError, AttributeError):
                detail = body_text or e.reason
            raise ApiClientError(str(detail), status_code=e.code) from e
        except urllib.error.URLError as e:
            raise ApiClientError(
                f"Cannot reach the backend at {self.base_url}. Is it running? ({e.reason})"
            ) from e

    # ------------------------------------------------------------------
    # Public verbs
    # ------------------------------------------------------------------
    def get(self, path: str, params: dict = None) -> dict:
        return self._request("GET", path, params=params)

    def get_raw(self, path: str, params: dict = None) -> bytes:
        """For endpoints that return a non-JSON body, e.g. ?format=csv."""
        return self._request("GET", path, params=params, raw=True)

    def post(self, path: str, payload: dict = None) -> dict:
        return self._request("POST", path, json_body=payload)

    def patch(self, path: str, payload: dict = None) -> dict:
        return self._request("PATCH", path, json_body=payload)

    def put(self, path: str, payload: dict = None) -> dict:
        return self._request("PUT", path, json_body=payload)

    def delete(self, path: str) -> dict:
        return self._request("DELETE", path)

    # ------------------------------------------------------------------
    # Envelope-aware convenience helpers
    # ------------------------------------------------------------------
    def get_data(self, path: str, params: dict = None):
        """GETs a single-item endpoint and unwraps {"data": ...}."""
        return self.get(path, params=params).get("data")

    def get_all_pages(self, path: str, params: dict = None, page_size: int = 100,
                       hard_cap: int = 5000) -> list:
        """Follows the {data, pagination} envelope across every page and
        returns the combined list. page_size is clamped to 100 — the
        backend's enforced maximum — regardless of what's requested, since
        a higher value fails the whole call with a 422 error. hard_cap is a
        safety limit on total results, independent of page_size."""
        params = dict(params or {})
        params["page_size"] = min(page_size, 100)
        page = 1
        results = []
        while True:
            params["page"] = page
            response = self.get(path, params=params)
            items = response.get("data") or []
            results.extend(items)
            pagination = response.get("pagination") or {}
            total = pagination.get("total", len(results))
            if not items or len(results) >= total or len(results) >= hard_cap:
                break
            page += 1
        return results


# Single shared instance imported by every service module.
api_client = ApiClient()
