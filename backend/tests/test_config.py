"""Settings worked out from other settings. No database is used."""

from app.config import cookie_secure


def test_cookie_is_secure_when_every_origin_is_https():
    assert cookie_secure(["https://example.com"])


def test_cookie_is_not_secure_on_plain_http():
    assert not cookie_secure(["http://localhost:5173"])
    assert not cookie_secure(["https://example.com", "http://localhost:5173"])
