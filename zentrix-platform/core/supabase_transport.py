from __future__ import annotations

import json
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from typing import Any


@dataclass
class SupabaseResponse:
    ok: bool
    status: int
    data: Any = None
    error: str = ""


class SupabaseRestClient:
    """Minimal Supabase HTTP client using only Python stdlib.

    Publishable keys are sent on ``apikey``. User JWTs, when present, are sent
    separately on ``Authorization`` so the new ``sb_publishable_`` format is
    never incorrectly treated as a Bearer JWT.
    """

    def __init__(self, url: str, publishable_key: str, access_token: str = "", timeout: float = 8.0) -> None:
        self.url = url.rstrip("/")
        self.publishable_key = publishable_key.strip()
        self.access_token = access_token.strip()
        self.timeout = timeout

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        headers = {
            "apikey": self.publishable_key,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        if self.access_token:
            headers["Authorization"] = f"Bearer {self.access_token}"
        if extra:
            headers.update(extra)
        return headers

    def request(
        self,
        method: str,
        path: str,
        *,
        query: dict[str, str] | None = None,
        body: Any = None,
        headers: dict[str, str] | None = None,
    ) -> SupabaseResponse:
        target = f"{self.url}{path if path.startswith('/') else '/' + path}"
        if query:
            target += "?" + urllib.parse.urlencode(query)
        payload = None if body is None else json.dumps(body).encode("utf-8")
        request = urllib.request.Request(
            target,
            data=payload,
            headers=self._headers(headers),
            method=method.upper(),
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                raw = response.read().decode("utf-8", errors="replace")
                data = json.loads(raw) if raw.strip() else None
                return SupabaseResponse(True, int(response.status), data=data)
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8", errors="replace")
            return SupabaseResponse(False, int(exc.code), error=raw[:1000])
        except (urllib.error.URLError, TimeoutError, OSError) as exc:
            return SupabaseResponse(False, 0, error=str(exc))

    def probe(self) -> SupabaseResponse:
        return self.request("GET", "/rest/v1/")

    def select(self, table: str, query: dict[str, str] | None = None) -> SupabaseResponse:
        params = {"select": "*"}
        if query:
            params.update(query)
        return self.request("GET", f"/rest/v1/{table}", query=params)

    def insert(self, table: str, row: dict[str, Any]) -> SupabaseResponse:
        return self.request(
            "POST",
            f"/rest/v1/{table}",
            body=row,
            headers={"Prefer": "return=representation"},
        )

    def update(self, table: str, filters: dict[str, str], values: dict[str, Any]) -> SupabaseResponse:
        return self.request(
            "PATCH",
            f"/rest/v1/{table}",
            query=filters,
            body=values,
            headers={"Prefer": "return=representation"},
        )

    def invoke_function(
        self,
        function_name: str,
        body: dict[str, Any],
        *,
        headers: dict[str, str] | None = None,
    ) -> SupabaseResponse:
        return self.request(
            "POST",
            f"/functions/v1/{function_name}",
            body=body,
            headers=headers,
        )
