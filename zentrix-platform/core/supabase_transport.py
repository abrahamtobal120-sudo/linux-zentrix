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
    """Minimal PostgREST client using only Python stdlib.

    The publishable/anon key is not treated as an administrative secret.
    Authorization must still be enforced by Supabase Auth + RLS.
    """

    def __init__(self, url: str, publishable_key: str, access_token: str = "", timeout: float = 8.0) -> None:
        self.url = url.rstrip("/")
        self.publishable_key = publishable_key.strip()
        self.access_token = access_token.strip()
        self.timeout = timeout

    def _headers(self, extra: dict[str, str] | None = None) -> dict[str, str]:
        auth = self.access_token or self.publishable_key
        headers = {
            "apikey": self.publishable_key,
            "Authorization": f"Bearer {auth}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
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
        # PostgREST root is enough to verify URL/key/network reachability without
        # requiring any application table to exist yet.
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
