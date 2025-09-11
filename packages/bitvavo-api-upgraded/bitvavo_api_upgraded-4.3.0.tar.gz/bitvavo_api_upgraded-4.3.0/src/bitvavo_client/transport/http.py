"""HTTP client for Bitvavo API."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any

import httpx
from returns.result import Failure, Result

from bitvavo_client.adapters.returns_adapter import (
    BitvavoError,
    decode_response_result,
)
from bitvavo_client.auth.signing import create_signature

if TYPE_CHECKING:  # pragma: no cover
    from bitvavo_client.auth.rate_limit import RateLimitManager
    from bitvavo_client.core.settings import BitvavoSettings
    from bitvavo_client.core.types import AnyDict


class HTTPClient:
    """HTTP client for Bitvavo REST API with rate limiting and authentication."""

    def __init__(self, settings: BitvavoSettings, rate_limiter: RateLimitManager) -> None:
        """Initialize HTTP client.

        Args:
            settings: Bitvavo settings configuration
            rate_limiter: Rate limit manager instance
        """
        self.settings: BitvavoSettings = settings
        self.rate_limiter: RateLimitManager = rate_limiter
        self._keys: list[tuple[str, str]] = [(item["key"], item["secret"]) for item in self.settings.api_keys]
        if not self._keys:
            msg = "API keys are required"
            raise ValueError(msg)

        for idx in range(len(self._keys)):
            self.rate_limiter.ensure_key(idx)

        self.key_index: int = 0
        self.api_key: str = ""
        self.api_secret: str = ""
        self._rate_limit_initialized: bool = False

        key, secret = self._keys[0]
        self.configure_key(key, secret, 0)

    def configure_key(self, key: str, secret: str, index: int) -> None:
        """Configure API key for authenticated requests.

        Args:
            key: API key
            secret: API secret
            index: Key index for rate limiting
        """
        self.api_key = key
        self.api_secret = secret
        self.key_index = index

    def select_key(self, index: int) -> None:
        """Select a specific API key by index."""
        if not (0 <= index < len(self._keys)):
            msg = "API key index out of range"
            raise IndexError(msg)
        key, secret = self._keys[index]
        self.configure_key(key, secret, index)

    def _rotate_key(self) -> bool:
        """Rotate to the next configured API key if available."""
        if len(self._keys) <= 1:
            return False

        next_idx = (self.key_index + 1) % len(self._keys)
        now = int(time.time() * 1000)
        reset_at = self.rate_limiter.get_reset_at(next_idx)

        if now < reset_at:
            self.rate_limiter.sleep_until_reset(next_idx)
            self.rate_limiter.reset_key(next_idx)
        elif self.rate_limiter.get_remaining(next_idx) <= self.rate_limiter.buffer:
            self.rate_limiter.reset_key(next_idx)

        self.select_key(next_idx)
        return True

    def request(
        self,
        method: str,
        endpoint: str,
        *,
        body: AnyDict | None = None,
        weight: int = 1,
    ) -> Result[Any, BitvavoError | httpx.HTTPError]:
        """Make HTTP request and return raw JSON data as a Result.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            body: Request body for POST/PUT requests
            weight: Rate limit weight of the request

        Returns:
            Result containing raw JSON response or error

        Raises:
            HTTPError: On transport-level failures
        """
        idx = self.key_index
        self._ensure_rate_limit_initialized()

        if not self.rate_limiter.has_budget(idx, weight):
            for _ in range(len(self._keys)):
                if self.rate_limiter.has_budget(idx, weight):
                    break
                rotated = self._rotate_key()
                idx = self.key_index
                if not rotated:
                    break
            if not self.rate_limiter.has_budget(idx, weight):
                self.rate_limiter.handle_limit(idx, weight)

        url = f"{self.settings.rest_url}{endpoint}"
        headers = self._create_auth_headers(method, endpoint, body)

        # Update rate limit usage for this call
        self.rate_limiter.record_call(idx, weight)

        try:
            response = self._make_http_request(method, url, headers, body)
        except httpx.HTTPError as exc:
            return Failure(exc)

        self._update_rate_limits(response, idx)
        # Always return raw data - let the caller handle model conversion
        return decode_response_result(response, model=Any)

    def _ensure_rate_limit_initialized(self) -> None:
        """Ensure the initial rate limit state is fetched from the API."""
        if self._rate_limit_initialized:
            return
        self._rate_limit_initialized = True
        self._initialize_rate_limit()

    def _initialize_rate_limit(self) -> None:
        """Fetch initial rate limit and handle potential rate limit errors."""
        endpoint = "/account"
        url = f"{self.settings.rest_url}{endpoint}"

        while True:
            headers = self._create_auth_headers("GET", endpoint, None)
            # Record the weight for this check (weight 1)
            self.rate_limiter.record_call(self.key_index, 1)

            try:
                response = self._make_http_request("GET", url, headers, None)
            except httpx.HTTPError:
                return

            self._update_rate_limits(response, self.key_index)

            err_code = ""
            if response.status_code == httpx.codes.TOO_MANY_REQUESTS:
                try:
                    data = response.json()
                except ValueError:
                    data = {}
                if isinstance(data, dict):
                    err = data.get("error")
                    if isinstance(err, dict):
                        err_code = str(err.get("code", ""))
            if response.status_code == httpx.codes.TOO_MANY_REQUESTS and err_code == "101":
                self.rate_limiter.sleep_until_reset(self.key_index)
                self.rate_limiter.reset_key(self.key_index)
                continue

            if self.rate_limiter.get_remaining(self.key_index) < self.rate_limiter.buffer:
                self.rate_limiter.sleep_until_reset(self.key_index)
                self.rate_limiter.reset_key(self.key_index)
                continue

            break

    def _create_auth_headers(self, method: str, endpoint: str, body: AnyDict | None) -> dict[str, str]:
        """Create authentication headers if API key is configured."""
        timestamp = int(time.time() * 1000) + self.settings.lag_ms
        signature = create_signature(timestamp, method, endpoint, body, self.api_secret)

        return {
            "bitvavo-access-key": self.api_key,
            "bitvavo-access-signature": signature,
            "bitvavo-access-timestamp": str(timestamp),
            "bitvavo-access-window": str(self.settings.access_window_ms),
        }

    def _make_http_request(
        self,
        method: str,
        url: str,
        headers: dict[str, str],
        body: AnyDict | None,
    ) -> httpx.Response:
        """Make the actual HTTP request."""
        timeout = self.settings.access_window_ms / 1000

        match method:
            case "GET":
                return httpx.get(url, headers=headers, timeout=timeout)
            case "POST":
                return httpx.post(url, headers=headers, json=body, timeout=timeout)
            case "PUT":
                return httpx.put(url, headers=headers, json=body, timeout=timeout)
            case "DELETE":
                return httpx.delete(url, headers=headers, timeout=timeout)
            case _:
                msg = f"Unsupported HTTP method: {method}"
                raise ValueError(msg)

    def _update_rate_limits(self, response: httpx.Response, idx: int) -> None:
        """Update rate limits based on response."""
        try:
            json_data = response.json()
        except ValueError:
            json_data = {}

        if isinstance(json_data, dict) and "error" in json_data:
            if self._is_rate_limit_error(response, json_data):
                self.rate_limiter.update_from_error(idx, json_data)
            else:
                self.rate_limiter.update_from_headers(idx, dict(response.headers))
        else:
            self.rate_limiter.update_from_headers(idx, dict(response.headers))

    def _is_rate_limit_error(self, response: httpx.Response, json_data: dict[str, Any]) -> bool:
        """Check if response indicates a rate limit error."""
        status = getattr(response, "status_code", None)
        if status == httpx.codes.TOO_MANY_REQUESTS:
            return True

        err = json_data.get("error")
        if isinstance(err, dict):
            code = str(err.get("code", "")).lower()
            message = str(err.get("message", "")).lower()
        else:
            code = ""
            message = str(err).lower()

        return any(k in code or k in message for k in ("rate", "limit", "too_many"))
