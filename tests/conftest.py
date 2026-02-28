import json
from pathlib import Path
from unittest.mock import patch

import pytest

_STATIC_CATALOG_PATH = Path(__file__).parent.parent / "app" / "data" / "services_catalog.json"


@pytest.fixture(autouse=True)
def mock_qdrant_catalog():
    """Patch _fetch_catalog_from_qdrant to return the static JSON so tests
    don't require a live Qdrant connection."""
    with open(_STATIC_CATALOG_PATH) as f:
        catalog = json.load(f)

    with patch("app.services.catalog._fetch_catalog_from_qdrant", return_value=catalog):
        # Reset the cached catalog so _load_catalog re-fetches via the mock
        import app.services.catalog as cat_mod
        cat_mod._CATALOG = None
        cat_mod._CATALOG_LOADED_AT = 0
        yield


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (requiring LLM)")
