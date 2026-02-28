from unittest.mock import patch

import pytest

_TEST_CATALOG = {
    "services": [
        {
            "category": "twitter_posts",
            "services": [
                {
                    "name": "Tweet Scraper",
                    "type": "apify",
                    "identifier": "test/tweet-scraper",
                    "api_slug": "test~tweet-scraper",
                    "initiators": ["keyword"],
                    "description": "Scrape tweets by keyword.",
                    "sample_input": {"searchTerms": ["{KEYWORD}"]},
                    "output_mapping": {"text": "description"},
                    "pagination": {"isEnabled": False},
                },
                {
                    "name": "Tweet Scraper by Hashtag",
                    "type": "apify",
                    "identifier": "test/tweet-scraper",
                    "api_slug": "test~tweet-scraper",
                    "initiators": ["hashtag"],
                    "description": "Scrape tweets by hashtag.",
                    "sample_input": {"searchTerms": ["#{HASHTAG}"]},
                    "output_mapping": {"text": "description"},
                    "pagination": {"isEnabled": False},
                },
                {
                    "name": "Tweet Scraper by URL",
                    "type": "apify",
                    "identifier": "test/tweet-scraper",
                    "api_slug": "test~tweet-scraper",
                    "initiators": ["url"],
                    "description": "Scrape tweets by URL.",
                    "sample_input": {"startUrls": ["{URL}"]},
                    "output_mapping": {"text": "description"},
                    "pagination": {"isEnabled": False},
                },
                {
                    "name": "Tweet Scraper by Username",
                    "type": "apify",
                    "identifier": "test/tweet-scraper-user",
                    "api_slug": "test~tweet-scraper-user",
                    "initiators": ["username"],
                    "description": "Scrape tweets by username.",
                    "sample_input": {"usernames": ["{USERNAME}"]},
                    "output_mapping": {"text": "description"},
                    "pagination": {"isEnabled": False},
                },
            ],
        },
        {
            "category": "instagram_posts",
            "services": [
                {
                    "name": "Instagram Scraper",
                    "type": "apify",
                    "identifier": "test/instagram-scraper",
                    "api_slug": "test~instagram-scraper",
                    "initiators": ["hashtag"],
                    "description": "Scrape Instagram posts by hashtag.",
                    "sample_input": {"hashtags": ["{HASHTAG}"]},
                    "output_mapping": {"caption": "description"},
                    "pagination": {"isEnabled": False},
                },
            ],
        },
        {
            "category": "photo_location",
            "services": [
                {
                    "name": "Photo Location Finder",
                    "type": "geospy",
                    "identifier": "test/photo-location",
                    "api_slug": "predict",
                    "initiators": ["image"],
                    "description": "Find location of a photo.",
                    "sample_input": {"image": "{IMAGE_URL}"},
                    "output_mapping": {"lat": "latitude", "lng": "longitude"},
                    "pagination": {"isEnabled": False},
                },
            ],
        },
    ],
}


@pytest.fixture(autouse=True)
def mock_qdrant_catalog():
    """Patch _fetch_catalog_from_qdrant to return a test fixture so tests
    don't require a live Qdrant connection."""
    with patch("app.services.catalog._fetch_catalog_from_qdrant", return_value=_TEST_CATALOG):
        # Reset the cached catalog so _load_catalog re-fetches via the mock
        import app.services.catalog as cat_mod
        cat_mod._CATALOG = None
        cat_mod._CATALOG_LOADED_AT = 0
        yield


def pytest_configure(config):
    config.addinivalue_line("markers", "slow: marks tests as slow (requiring LLM)")
