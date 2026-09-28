"""HTTP handlers for the V3 product API."""

from __future__ import annotations

import json
import os
import socket
from typing import Any, Dict
from urllib.error import HTTPError, URLError
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit
from urllib.request import Request, urlopen

_MAX_RESPONSE_BYTES = 10 * 1024 * 1024


def _json_result(payload: Dict[str, Any]) -> str:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))


def _api_endpoint() -> str:
    configured = os.environ.get("V3_API_BASE_URL", "").strip().rstrip("/")
    if not configured:
        raise ValueError("V3_API_BASE_URL is not configured")

    parsed = urlsplit(configured)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise ValueError("V3_API_BASE_URL must be an absolute http(s) URL")

    path = parsed.path.rstrip("/")
    if not path or path == "/":
        path = "/index.php"

    return urlunsplit((parsed.scheme, parsed.netloc, path, parsed.query, ""))


def _timeout() -> float:
    raw = os.environ.get("V3_API_TIMEOUT_SECONDS", "20").strip()
    try:
        return max(1.0, min(float(raw), 120.0))
    except ValueError:
        return 20.0


def _request(api: str, params: Dict[str, Any], method: str = "GET") -> str:
    token = os.environ.get("V3_API_TOKEN", "").strip()
    if not token:
        return _json_result({"ok": False, "error": "V3_API_TOKEN is not configured"})

    try:
        endpoint = _api_endpoint()
    except ValueError as exc:
        return _json_result({"ok": False, "error": str(exc)})

    parsed = urlsplit(endpoint)
    query = dict(parse_qsl(parsed.query, keep_blank_values=True))
    query.update({"api": api, **params})
    url = urlunsplit(
        (parsed.scheme, parsed.netloc, parsed.path, urlencode(query), "")
    )
    request = Request(
        url,
        data=b"" if method == "POST" else None,
        method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/json",
            "User-Agent": "Hermes-V3-Product-Plugin/1.0",
        },
    )

    try:
        with urlopen(request, timeout=_timeout()) as response:
            body = response.read(_MAX_RESPONSE_BYTES + 1)
            if len(body) > _MAX_RESPONSE_BYTES:
                return _json_result(
                    {"ok": False, "error": "V3 API response exceeded 10 MiB"}
                )
            charset = response.headers.get_content_charset() or "utf-8"
            text = body.decode(charset, errors="replace")
            try:
                payload = json.loads(text)
            except json.JSONDecodeError:
                return _json_result(
                    {
                        "ok": False,
                        "status": response.status,
                        "error": "V3 API returned a non-JSON response",
                    }
                )
            return _json_result(
                {"ok": 200 <= response.status < 300, "status": response.status, "response": payload}
            )
    except HTTPError as exc:
        body = exc.read(_MAX_RESPONSE_BYTES).decode("utf-8", errors="replace")
        try:
            detail: Any = json.loads(body)
        except json.JSONDecodeError:
            detail = body[:1000]
        return _json_result(
            {"ok": False, "status": exc.code, "error": "V3 API request failed", "response": detail}
        )
    except (URLError, socket.timeout, TimeoutError) as exc:
        reason = getattr(exc, "reason", exc)
        return _json_result(
            {"ok": False, "error": f"Unable to reach V3 API: {reason}"}
        )
    except Exception as exc:  # Keep plugin failures visible to the model without crashing Hermes.
        return _json_result(
            {"ok": False, "error": f"Unexpected V3 API error: {type(exc).__name__}"}
        )


def search_products(params: Dict[str, Any], **kwargs: Any) -> str:
    """Search products by text, product number, SKU name, or barcode."""
    del kwargs
    keyword = str(params.get("keyword", "")).strip()
    if not keyword:
        return _json_result({"ok": False, "error": "keyword is required"})

    limit = max(1, min(int(params.get("limit", 10)), 20))
    query: Dict[str, Any] = {"keyword": keyword[:100], "limit": limit}
    if params.get("store_id") is not None:
        store_id = int(params["store_id"])
        if store_id > 0:
            query["store_id"] = store_id

    return _request("external.HarnessData.search", query)


def get_product_detail(params: Dict[str, Any], **kwargs: Any) -> str:
    """Return product, SKU/configuration, inventory, price, and image data."""
    del kwargs
    product_id = int(params.get("product_id", 0))
    if product_id < 1:
        return _json_result({"ok": False, "error": "product_id must be a positive integer"})

    return _request(
        "external.HarnessData.detail",
        {"product_id": product_id},
        method="POST",
    )

