"""Test setup. pytest runs this file before it collects any tests."""

import os

# app.config requires DATABASE_URL. A placeholder lets the tests run without
# a .env file. Nothing connects to it: creating the engine does not open a
# connection, and no test runs a query. A value already set in the shell is
# kept, and an empty one counts as unset.
if not os.environ.get("DATABASE_URL", "").strip():
    os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
