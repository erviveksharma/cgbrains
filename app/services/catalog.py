import logging
import time
from collections import defaultdict

from qdrant_client import QdrantClient

from app.config import settings

logger = logging.getLogger(__name__)

_CATALOG: dict | None = None
_CATALOG_LOADED_AT: float = 0
_CACHE_TTL: int = 300  # 5 minutes


def _get_qdrant_client() -> QdrantClient:
    return QdrantClient(
        url=settings.qdrant_url,
        api_key=settings.qdrant_api_key or None,
    )


def _fetch_catalog_from_qdrant() -> dict:
    """Scroll all points from the Qdrant collection and group by category."""
    client = _get_qdrant_client()

    grouped: dict[str, list[dict]] = defaultdict(list)
    offset = None

    while True:
        results, next_offset = client.scroll(
            collection_name=settings.qdrant_collection,
            limit=100,
            offset=offset,
            with_payload=True,
            with_vectors=False,
        )

        for point in results:
            payload = point.payload
            category = payload.get("category", "unknown")
            service = {k: v for k, v in payload.items() if k != "category"}
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


def find_service(category: str, initiator: str | None = None) -> dict | None:
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
