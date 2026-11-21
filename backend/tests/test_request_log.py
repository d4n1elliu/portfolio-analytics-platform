"""The line logged for each request. No database is used."""

import logging

from fastapi.testclient import TestClient

from app.main import app
from app.request_log import describe_request


def logged_lines(caplog) -> list[str]:
    return [record.getMessage() for record in caplog.records if record.name == "app.requests"]


def test_a_request_is_described_by_its_method_path_status_and_time():
    assert describe_request("GET", "/trades", 200, 0.0123) == "GET /trades 200 12ms"


def test_each_request_is_logged_without_its_query_string(caplog):
    caplog.set_level(logging.INFO, logger="app.requests")

    TestClient(app).get("/trades", params={"ticker": "BHP"})

    (line,) = logged_lines(caplog)
    assert line.startswith("GET /trades 401 ")
    assert "BHP" not in line


def test_the_health_check_is_not_logged(caplog):
    caplog.set_level(logging.INFO, logger="app.requests")

    TestClient(app).get("/health")

    assert logged_lines(caplog) == []
