"""Run the API suite in per-test schemas of a separate PostgreSQL test database."""

import os
import pytest
from sqlalchemy.engine import make_url
from app.core.config import DATABASE_URL

if __name__ == "__main__":
    url = make_url(DATABASE_URL)
    if url.get_backend_name() != "postgresql":
        raise SystemExit("Configure PostgreSQL before running this suite")
    os.environ["TEST_DATABASE_URL"] = url.set(
        database="distriflow_module_tests"
    ).render_as_string(hide_password=False)
    raise SystemExit(pytest.main(["-q", "--tb=short"]))
