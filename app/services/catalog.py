import json
from pathlib import Path

_CATALOG: dict | None = None
_CATALOG_PATH = Path(__file__).parent.parent / "data" / "services_catalog.json"


def _load_catalog() -> dict:
    global _CATALOG
    if _CATALOG is None:
        with open(_CATALOG_PATH) as f:
            _CATALOG = json.load(f)
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
    """Force reload the catalog from disk."""
    global _CATALOG
    _CATALOG = None
    _load_catalog()
