# tests/conftest.py — Use separate test database
import os

os.environ["DATABASE_URL"] = "sqlite:///./test_guest_services.db"
