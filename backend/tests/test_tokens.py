"""Session tokens. No database is used."""

from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.config import cookie_secure
from app.services.tokens import ALGORITHM, InvalidTokenError, create_token, read_token

NOW = datetime.now(UTC)


def test_token_gives_back_the_user_id():
    assert read_token(create_token(42, NOW)) == 42


def test_expired_token_is_rejected():
    token = create_token(42, NOW - timedelta(minutes=61), minutes=60)

    with pytest.raises(InvalidTokenError):
        read_token(token)


def test_token_is_accepted_until_it_expires():
    token = create_token(42, NOW - timedelta(minutes=59), minutes=60)

    assert read_token(token) == 42


def test_token_changed_to_another_user_is_rejected():
    header, _, signature = create_token(42, NOW).split(".")
    _, other_claims, _ = create_token(7, NOW).split(".")

    with pytest.raises(InvalidTokenError):
        read_token(f"{header}.{other_claims}.{signature}")


def test_token_signed_with_another_secret_is_rejected():
    claims = {"sub": "42", "exp": NOW + timedelta(minutes=60)}
    token = jwt.encode(claims, "a-different-secret-that-is-long-enough", algorithm=ALGORITHM)

    with pytest.raises(InvalidTokenError):
        read_token(token)


def test_token_with_no_signature_is_rejected():
    claims = {"sub": "42", "exp": NOW + timedelta(minutes=60)}
    token = jwt.encode(claims, None, algorithm="none")

    with pytest.raises(InvalidTokenError):
        read_token(token)


def test_token_with_no_expiry_is_rejected():
    token = jwt.encode({"sub": "42"}, "test-secret-that-is-long-enough-for-hs256", ALGORITHM)

    with pytest.raises(InvalidTokenError):
        read_token(token)


def test_token_with_no_user_is_rejected():
    claims = {"exp": NOW + timedelta(minutes=60)}
    token = jwt.encode(claims, "test-secret-that-is-long-enough-for-hs256", ALGORITHM)

    with pytest.raises(InvalidTokenError):
        read_token(token)


@pytest.mark.parametrize("token", ["", "not-a-token", "a.b.c"])
def test_text_that_is_not_a_token_is_rejected(token):
    with pytest.raises(InvalidTokenError):
        read_token(token)


def test_cookie_is_secure_when_every_origin_is_https():
    assert cookie_secure(["https://example.com"])


def test_cookie_is_not_secure_on_plain_http():
    assert not cookie_secure(["http://localhost:5173"])
    assert not cookie_secure(["https://example.com", "http://localhost:5173"])
