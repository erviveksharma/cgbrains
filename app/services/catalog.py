import logging
import time
from collections import defaultdict
from typing import Optional

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

_CATALOG: Optional[dict] = None
_CATALOG_LOADED_AT: float = 0
_CACHE_TTL: int = 300  # 5 minutes


def _qdrant_scroll(collection: str, limit: int = 100, offset=None) -> tuple[list, Optional[str]]:
    """Scroll points from Qdrant using the REST API directly (bypasses qdrant-client IPv4 issues)."""
    url = f"{settings.qdrant_url}/collections/{collection}/points/scroll"
    headers = {"Content-Type": "application/json"}
    if settings.qdrant_api_key:
        headers["api-key"] = settings.qdrant_api_key

    body = {"limit": limit, "with_payload": True, "with_vector": False}
    if offset is not None:
        body["offset"] = offset

    resp = httpx.post(url, json=body, headers=headers, timeout=30)
    resp.raise_for_status()
    data = resp.json()["result"]
    return data["points"], data.get("next_page_offset")


def _fetch_catalog_from_qdrant() -> dict:
    """Scroll all points from the Qdrant collection and group by category.

    Each Qdrant point stores service fields under ``payload.metadata`` with a
    singular ``initiator`` string.  Each point is its own service entry
    (different points may have different sample_input, description, or even
    category), so we convert ``initiator`` -> ``initiators`` list and group
    by category.
    """
    grouped: dict[str, list[dict]] = defaultdict(list)
    offset = None

    while True:
        results, next_offset = _qdrant_scroll(settings.qdrant_collection, limit=100, offset=offset)

        for point in results:
            payload = point.get("payload", {})
            meta = payload.get("metadata", payload)
            category = meta.get("category", "unknown")
            initiator = meta.get("initiator")

            service = {
                k: v for k, v in meta.items()
                if k not in ("category", "initiator", "source", "blobType", "loc")
            }
            service["initiators"] = [initiator] if initiator else []
            grouped[category].append(service)

        if next_offset is None:
            break
        offset = next_offset

    catalog = {
        "services": [
            {"category": cat, "services": svcs}
            for cat, svcs in sorted(grouped.items())
        ]
    }
    return catalog


def _load_catalog() -> dict:
    global _CATALOG, _CATALOG_LOADED_AT

    now = time.monotonic()
    if _CATALOG is not None and (now - _CATALOG_LOADED_AT) < _CACHE_TTL:
        return _CATALOG

    try:
        catalog = _fetch_catalog_from_qdrant()
        _CATALOG = catalog
        _CATALOG_LOADED_AT = now
        logger.info("Loaded service catalog from Qdrant (%d categories)", len(catalog["services"]))
    except Exception:
        if _CATALOG is not None:
            logger.warning("Failed to refresh catalog from Qdrant, using stale cache", exc_info=True)
        else:
            logger.error("Failed to load catalog from Qdrant and no cache available", exc_info=True)
            raise

    return _CATALOG


def get_services_summary() -> str:
    """Return a condensed text summary of all services for the LLM system prompt."""
    catalog = _load_catalog()
    lines = ["AVAILABLE SERVICES (use [service] step):"]

    for category_group in catalog["services"]:
        category = category_group["category"]
        service_parts = []
        for svc in category_group["services"]:
            initiators = "|".join(svc["initiators"])
            service_parts.append(f"{svc['name']} ({initiators})")
        lines.append(f"  {category}: {' | '.join(service_parts)}")

    return "\n".join(lines)


def find_service(category: str, initiator: Optional[str] = None) -> Optional[dict]:
    """Find a service by category and optional initiator type."""
    catalog = _load_catalog()

    for category_group in catalog["services"]:
        if category_group["category"] == category:
            if initiator is None:
                return category_group["services"][0]
            for svc in category_group["services"]:
                if initiator in svc["initiators"]:
                    return svc
            # Fallback: return first service in category
            return category_group["services"][0]

    return None


def list_categories() -> list[dict]:
    """Return all service categories with their available initiators."""
    catalog = _load_catalog()
    result = []

    for category_group in catalog["services"]:
        all_initiators = set()
        for svc in category_group["services"]:
            all_initiators.update(svc["initiators"])
        result.append({
            "category": category_group["category"],
            "services": category_group["services"],
            "initiators": sorted(all_initiators),
        })

    return result


def reload_catalog() -> None:
    """Force reload the catalog from Qdrant."""
    global _CATALOG, _CATALOG_LOADED_AT
    _CATALOG = None
    _CATALOG_LOADED_AT = 0
    _load_catalog()
