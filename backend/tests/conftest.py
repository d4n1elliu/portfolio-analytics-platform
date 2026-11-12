"""Test setup. pytest runs this file before it collects any tests."""

import os

# app.config requires DATABASE_URL. A placeholder lets the tests run without
# a .env file and guarantees they never touch a real database.
os.environ["DATABASE_URL"] = "postgresql://test:test@localhost:5432/test"
