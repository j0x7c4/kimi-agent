"""Tests for branding API — Pydantic model validation, CRUD functions, and endpoints."""

from __future__ import annotations

import base64
import sqlite3

import pytest
from pydantic import ValidationError

from kimi_cli.web.api.branding import BrandingResponse, UpdateBrandingRequest
from kimi_cli.web.db.crud import (
    BRANDING_KEYS,
    delete_all_branding,
    get_branding,
    upsert_branding,
)

# ---------------------------------------------------------------------------
# Test helpers
# ---------------------------------------------------------------------------

# Smallest valid 1x1 transparent PNG (68 bytes).
_TINY_PNG_BYTES = (
    b"\x89PNG\r\n\x1a\n"
    b"\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89"
    b"\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01"
    b"\r\n\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)
_TINY_PNG_B64 = base64.b64encode(_TINY_PNG_BYTES).decode()

# Valid Data URLs for logo / favicon tests.
VALID_LOGO_DATA_URL = f"data:image/png;base64,{_TINY_PNG_B64}"
VALID_FAVICON_DATA_URL = f"data:image/png;base64,{_TINY_PNG_B64}"
VALID_SVG_LOGO_DATA_URL = f"data:image/svg+xml;base64,{_TINY_PNG_B64}"
VALID_ICO_FAVICON_DATA_URL = f"data:image/x-icon;base64,{_TINY_PNG_B64}"


def _make_branding_db(*, check_same_thread: bool = True) -> sqlite3.Connection:
    """Create an in-memory SQLite database with the branding table."""
    conn = sqlite3.connect(":memory:", check_same_thread=check_same_thread)
    conn.row_factory = sqlite3.Row
    conn.execute(
        """
        CREATE TABLE branding (
            key   TEXT PRIMARY KEY,
            value TEXT NOT NULL
        )
        """
    )
    conn.commit()
    return conn


# =========================================================================
# 1. Pydantic Model Validation Tests
# =========================================================================


class TestUpdateBrandingRequestValidation:
    """Pydantic model validation for UpdateBrandingRequest."""

    # ----- happy paths -----

    def test_valid_full_request(self) -> None:
        req = UpdateBrandingRequest(
            brand_name="Acme Corp",
            version="1.2.3",
            page_title="Acme Dashboard",
            logo_url="https://acme.example.com",
            logo=VALID_LOGO_DATA_URL,
            favicon=VALID_FAVICON_DATA_URL,
        )
        assert req.brand_name == "Acme Corp"
        assert req.version == "1.2.3"
        assert req.page_title == "Acme Dashboard"
        assert req.logo_url == "https://acme.example.com"
        assert req.logo == VALID_LOGO_DATA_URL
        assert req.favicon == VALID_FAVICON_DATA_URL

    def test_all_none_is_valid(self) -> None:
        """Passing all fields as None is valid — it means 'reset everything'."""
        req = UpdateBrandingRequest(
            brand_name=None,
            version=None,
            page_title=None,
            logo_url=None,
            logo=None,
            favicon=None,
        )
        assert req.brand_name is None
        assert req.version is None
        assert req.page_title is None
        assert req.logo_url is None
        assert req.logo is None
        assert req.favicon is None

    def test_empty_body_is_valid(self) -> None:
        """An empty body (all defaults) is valid — fields default to None."""
        req = UpdateBrandingRequest()
        for field in ("brand_name", "version", "page_title", "logo_url", "logo", "favicon"):
            assert getattr(req, field) is None, f"{field} should default to None"

    def test_logo_url_with_http(self) -> None:
        req = UpdateBrandingRequest(logo_url="http://example.com/logo.png")
        assert req.logo_url == "http://example.com/logo.png"

    def test_logo_svg_mime(self) -> None:
        req = UpdateBrandingRequest(logo=VALID_SVG_LOGO_DATA_URL)
        assert req.logo == VALID_SVG_LOGO_DATA_URL

    def test_favicon_ico_mime(self) -> None:
        req = UpdateBrandingRequest(favicon=VALID_ICO_FAVICON_DATA_URL)
        assert req.favicon == VALID_ICO_FAVICON_DATA_URL

    # ----- field length limits -----

    def test_brand_name_exceeding_30_chars(self) -> None:
        with pytest.raises(ValidationError, match="brand_name must be <= 30 characters"):
            UpdateBrandingRequest(brand_name="x" * 31)

    def test_brand_name_exactly_30_chars(self) -> None:
        req = UpdateBrandingRequest(brand_name="x" * 30)
        assert len(req.brand_name) == 30

    def test_version_exceeding_20_chars(self) -> None:
        with pytest.raises(ValidationError, match="version must be <= 20 characters"):
            UpdateBrandingRequest(version="v" * 21)

    def test_version_exactly_20_chars(self) -> None:
        req = UpdateBrandingRequest(version="v" * 20)
        assert len(req.version) == 20

    def test_page_title_exceeding_60_chars(self) -> None:
        with pytest.raises(ValidationError, match="page_title must be <= 60 characters"):
            UpdateBrandingRequest(page_title="t" * 61)

    def test_page_title_exactly_60_chars(self) -> None:
        req = UpdateBrandingRequest(page_title="t" * 60)
        assert len(req.page_title) == 60

    # ----- logo_url scheme -----

    def test_logo_url_without_http_prefix(self) -> None:
        with pytest.raises(
            ValidationError, match="logo_url must start with http:// or https://"
        ):
            UpdateBrandingRequest(logo_url="ftp://example.com/logo.png")

    def test_logo_url_bare_domain(self) -> None:
        with pytest.raises(ValidationError, match="logo_url must start with"):
            UpdateBrandingRequest(logo_url="example.com")

    # ----- logo MIME validation -----

    def test_logo_invalid_mime_gif(self) -> None:
        bad = f"data:image/gif;base64,{_TINY_PNG_B64}"
        with pytest.raises(ValidationError, match="logo must be a valid Data URL"):
            UpdateBrandingRequest(logo=bad)

    def test_logo_invalid_mime_webp(self) -> None:
        bad = f"data:image/webp;base64,{_TINY_PNG_B64}"
        with pytest.raises(ValidationError, match="logo must be a valid Data URL"):
            UpdateBrandingRequest(logo=bad)

    def test_logo_plain_url_rejected(self) -> None:
        """A regular URL (not a Data URL) should be rejected for the logo field."""
        with pytest.raises(ValidationError, match="logo must be a valid Data URL"):
            UpdateBrandingRequest(logo="https://example.com/logo.png")

    # ----- favicon MIME validation -----

    def test_favicon_invalid_mime_gif(self) -> None:
        bad = f"data:image/gif;base64,{_TINY_PNG_B64}"
        with pytest.raises(ValidationError, match="favicon must be a valid Data URL"):
            UpdateBrandingRequest(favicon=bad)

    def test_favicon_invalid_mime_jpeg(self) -> None:
        """JPEG is allowed for logo but NOT for favicon."""
        bad = f"data:image/jpeg;base64,{_TINY_PNG_B64}"
        with pytest.raises(ValidationError, match="favicon must be a valid Data URL"):
            UpdateBrandingRequest(favicon=bad)

    # ----- base64 size limits -----

    def test_logo_oversized_base64(self) -> None:
        """Logo decoded payload > 512 KB should be rejected."""
        # Generate payload slightly over 512 KB.
        big_bytes = b"\x00" * (512 * 1024 + 1)
        big_b64 = base64.b64encode(big_bytes).decode()
        data_url = f"data:image/png;base64,{big_b64}"
        with pytest.raises(ValidationError, match="logo decoded size exceeds 512 KB"):
            UpdateBrandingRequest(logo=data_url)

    def test_favicon_oversized_base64(self) -> None:
        """Favicon decoded payload > 256 KB should be rejected."""
        big_bytes = b"\x00" * (256 * 1024 + 1)
        big_b64 = base64.b64encode(big_bytes).decode()
        data_url = f"data:image/png;base64,{big_b64}"
        with pytest.raises(ValidationError, match="favicon decoded size exceeds 256 KB"):
            UpdateBrandingRequest(favicon=data_url)

    def test_logo_exactly_512kb_accepted(self) -> None:
        """Logo of exactly 512 KB should be accepted."""
        exact_bytes = b"\x00" * (512 * 1024)
        exact_b64 = base64.b64encode(exact_bytes).decode()
        data_url = f"data:image/png;base64,{exact_b64}"
        req = UpdateBrandingRequest(logo=data_url)
        assert req.logo is not None

    def test_favicon_exactly_256kb_accepted(self) -> None:
        """Favicon of exactly 256 KB should be accepted."""
        exact_bytes = b"\x00" * (256 * 1024)
        exact_b64 = base64.b64encode(exact_bytes).decode()
        data_url = f"data:image/png;base64,{exact_b64}"
        req = UpdateBrandingRequest(favicon=data_url)
        assert req.favicon is not None


# =========================================================================
# 2. BrandingResponse Model Tests
# =========================================================================


class TestBrandingResponse:
    """Basic tests for the response model."""

    def test_all_none_response(self) -> None:
        resp = BrandingResponse()
        for field in ("brand_name", "version", "page_title", "logo_url", "logo", "favicon"):
            assert getattr(resp, field) is None

    def test_populated_response(self) -> None:
        resp = BrandingResponse(brand_name="Test", version="1.0")
        assert resp.brand_name == "Test"
        assert resp.version == "1.0"
        assert resp.logo is None


# =========================================================================
# 3. CRUD Function Tests
# =========================================================================


class TestBrandingCRUD:
    """Database CRUD function tests using an in-memory SQLite database."""

    @pytest.fixture()
    def db(self) -> sqlite3.Connection:
        """Create an in-memory SQLite database with the branding table."""
        conn = _make_branding_db()
        yield conn
        conn.close()

    # ----- get_branding -----

    def test_get_branding_empty_table(self, db: sqlite3.Connection) -> None:
        """An empty branding table should return all keys with None values."""
        result = get_branding(db)
        assert set(result.keys()) == BRANDING_KEYS, "Should contain all branding keys"
        for key in BRANDING_KEYS:
            assert result[key] is None, f"Key '{key}' should be None on empty table"

    # ----- upsert_branding -----

    def test_upsert_inserts_new_values(self, db: sqlite3.Connection) -> None:
        """upsert_branding should insert new rows for keys that don't exist yet."""
        upsert_branding(db, {"brand_name": "Acme", "version": "2.0"})
        result = get_branding(db)
        assert result["brand_name"] == "Acme"
        assert result["version"] == "2.0"
        # Other keys remain None.
        assert result["page_title"] is None
        assert result["logo"] is None

    def test_upsert_updates_existing_values(self, db: sqlite3.Connection) -> None:
        """upsert_branding should overwrite existing values (idempotent)."""
        upsert_branding(db, {"brand_name": "V1"})
        upsert_branding(db, {"brand_name": "V2"})
        result = get_branding(db)
        assert result["brand_name"] == "V2", "Second upsert should overwrite the first"

    def test_upsert_none_deletes_key(self, db: sqlite3.Connection) -> None:
        """upsert_branding with None value should delete that key."""
        upsert_branding(db, {"brand_name": "Acme"})
        assert get_branding(db)["brand_name"] == "Acme"

        upsert_branding(db, {"brand_name": None})
        assert get_branding(db)["brand_name"] is None, "None should delete the key"

    def test_upsert_empty_string_deletes_key(self, db: sqlite3.Connection) -> None:
        """upsert_branding with empty string value should also delete the key."""
        upsert_branding(db, {"brand_name": "Acme"})
        upsert_branding(db, {"brand_name": ""})
        assert get_branding(db)["brand_name"] is None

    def test_upsert_ignores_unknown_keys(self, db: sqlite3.Connection) -> None:
        """Keys not in BRANDING_KEYS should be silently ignored."""
        upsert_branding(db, {"unknown_key": "value", "brand_name": "OK"})
        result = get_branding(db)
        assert result["brand_name"] == "OK"
        assert "unknown_key" not in result

    # ----- delete_all_branding -----

    def test_delete_all_branding(self, db: sqlite3.Connection) -> None:
        """delete_all_branding should remove every row."""
        upsert_branding(db, {
            "brand_name": "Acme",
            "version": "1.0",
            "page_title": "Title",
        })
        delete_all_branding(db)
        result = get_branding(db)
        for key in BRANDING_KEYS:
            assert result[key] is None, f"'{key}' should be None after delete_all"

    def test_delete_all_on_empty_table(self, db: sqlite3.Connection) -> None:
        """delete_all_branding on an already-empty table should not raise."""
        delete_all_branding(db)  # Should not raise.
        result = get_branding(db)
        assert all(v is None for v in result.values())

    # ----- round-trip -----

    def test_roundtrip_upsert_then_get(self, db: sqlite3.Connection) -> None:
        """Values written by upsert should be readable by get_branding."""
        settings = {
            "brand_name": "RoundTrip Corp",
            "version": "3.14",
            "page_title": "RT Dashboard",
            "logo_url": "https://rt.example.com",
            "logo": VALID_LOGO_DATA_URL,
            "favicon": VALID_FAVICON_DATA_URL,
        }
        upsert_branding(db, settings)
        result = get_branding(db)
        for key, expected in settings.items():
            assert result[key] == expected, f"Round-trip mismatch for '{key}'"

    def test_partial_update_preserves_other_keys(self, db: sqlite3.Connection) -> None:
        """Updating one key should not affect other existing keys."""
        upsert_branding(db, {"brand_name": "A", "version": "1"})
        upsert_branding(db, {"version": "2"})
        result = get_branding(db)
        assert result["brand_name"] == "A", "brand_name should be untouched"
        assert result["version"] == "2", "version should be updated"


# =========================================================================
# 4. API Endpoint Tests (integration via FastAPI TestClient)
# =========================================================================

# These tests verify the HTTP layer. They monkeypatch `get_db` to use an
# in-memory database and bypass the `require_admin` dependency so that
# endpoint wiring, serialization, and status codes are exercised without
# needing real auth infrastructure.


class TestBrandingEndpoints:
    """Integration tests for branding API endpoints using FastAPI TestClient."""

    @pytest.fixture()
    def client(self):
        """Build a minimal FastAPI app with branding routers and an in-memory DB."""
        from unittest.mock import patch

        from fastapi import FastAPI
        from fastapi.testclient import TestClient

        from kimi_cli.web.api.branding import admin_router, public_router

        app = FastAPI()
        app.include_router(public_router)
        app.include_router(admin_router)

        # Shared in-memory DB connection for the duration of one test.
        # check_same_thread=False is required because FastAPI TestClient
        # runs async handlers in a separate thread.
        conn = _make_branding_db(check_same_thread=False)

        # Override require_admin so it always succeeds.
        async def _fake_admin():
            return {"id": "test-admin", "role": "admin"}

        app.dependency_overrides = {}
        from kimi_cli.web.user_auth import require_admin

        app.dependency_overrides[require_admin] = _fake_admin

        # Patch get_db to return our in-memory connection as a context manager.
        from contextlib import contextmanager

        @contextmanager
        def _fake_get_db():
            yield conn

        with patch("kimi_cli.web.api.branding.get_db", _fake_get_db):
            yield TestClient(app)

        conn.close()

    # ----- GET /api/branding (public) -----

    def test_get_public_branding_empty(self, client) -> None:
        resp = client.get("/api/branding")
        assert resp.status_code == 200
        data = resp.json()
        for key in BRANDING_KEYS:
            assert data[key] is None, f"'{key}' should be None on empty DB"

    # ----- PUT /api/admin/branding -----

    def test_put_branding_valid(self, client) -> None:
        resp = client.put(
            "/api/admin/branding",
            json={"brand_name": "TestBrand", "version": "0.1"},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["brand_name"] == "TestBrand"
        assert data["version"] == "0.1"

    def test_put_branding_validation_error(self, client) -> None:
        """Exceeding field length should return 422 Unprocessable Entity."""
        resp = client.put(
            "/api/admin/branding",
            json={"brand_name": "x" * 31},
        )
        assert resp.status_code == 422
        body = resp.json()
        # FastAPI wraps validation errors in a "detail" list.
        assert "detail" in body

    def test_put_branding_invalid_logo_url(self, client) -> None:
        resp = client.put(
            "/api/admin/branding",
            json={"logo_url": "not-a-url"},
        )
        assert resp.status_code == 422

    def test_put_branding_invalid_logo_mime(self, client) -> None:
        bad_logo = f"data:image/gif;base64,{_TINY_PNG_B64}"
        resp = client.put(
            "/api/admin/branding",
            json={"logo": bad_logo},
        )
        assert resp.status_code == 422

    # ----- GET /api/admin/branding -----

    def test_get_admin_branding_reflects_put(self, client) -> None:
        """After a PUT, GET /api/admin/branding should return the updated values."""
        client.put(
            "/api/admin/branding",
            json={"page_title": "New Title"},
        )
        resp = client.get("/api/admin/branding")
        assert resp.status_code == 200
        assert resp.json()["page_title"] == "New Title"

    # ----- DELETE /api/admin/branding -----

    def test_delete_resets_branding(self, client) -> None:
        """DELETE should clear all branding; subsequent GET returns all None."""
        client.put(
            "/api/admin/branding",
            json={"brand_name": "Temp", "version": "9.9"},
        )
        resp = client.delete("/api/admin/branding")
        assert resp.status_code == 204

        get_resp = client.get("/api/branding")
        assert get_resp.status_code == 200
        data = get_resp.json()
        for key in BRANDING_KEYS:
            assert data[key] is None, f"'{key}' should be None after DELETE reset"

    # ----- PUT with null clears individual keys -----

    def test_put_null_clears_key(self, client) -> None:
        client.put(
            "/api/admin/branding",
            json={"brand_name": "Keep", "version": "1.0"},
        )
        # Now clear version by sending null.
        resp = client.put(
            "/api/admin/branding",
            json={"version": None},
        )
        assert resp.status_code == 200
        data = resp.json()
        # brand_name was also sent as None (default) so it gets cleared too —
        # this is the expected behaviour of model_dump() returning all fields.
        assert data["version"] is None
