"""Settings worked out from other settings. No database is used."""

import pytest

from app.config import _optional_flag, cookie_secure


def test_cookie_is_secure_when_every_origin_is_https():
    assert cookie_secure(["https://example.com"])


def test_cookie_is_not_secure_on_plain_http():
    assert not cookie_secure(["http://localhost:5173"])
    assert not cookie_secure(["https://example.com", "http://localhost:5173"])


@pytest.mark.parametrize("value", ["true", "TRUE", "1", "yes", "on", " true "])
def test_a_flag_is_on_for_the_usual_ways_of_saying_yes(monkeypatch, value):
    monkeypatch.setenv("A_TEST_FLAG", value)

    assert _optional_flag("A_TEST_FLAG")


@pytest.mark.parametrize("value", ["", "false", "0", "no", "off", "maybe"])
def test_a_flag_is_off_for_anything_else(monkeypatch, value):
    monkeypatch.setenv("A_TEST_FLAG", value)

    assert not _optional_flag("A_TEST_FLAG")


def test_a_flag_that_is_not_set_is_off(monkeypatch):
    monkeypatch.delenv("A_TEST_FLAG", raising=False)

    assert not _optional_flag("A_TEST_FLAG")
