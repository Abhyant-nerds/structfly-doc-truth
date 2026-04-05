import re


def _normalize_key(raw_key):
    return re.sub(r"[^a-z0-9]+", "_", raw_key.strip().lower()).strip("_")


def extract_key_value_pairs(bundle):
    text = bundle.get("text", "") if isinstance(bundle, dict) else str(bundle)
    pairs = []
    seen = set()

    for line in text.splitlines():
        if ":" not in line:
            continue

        raw_key, raw_value = line.split(":", 1)
        normalized_key = _normalize_key(raw_key)
        cleaned_value = raw_value.strip()
        if not normalized_key or not cleaned_value:
            continue

        key = (normalized_key, cleaned_value.lower())
        if key in seen:
            continue

        seen.add(key)
        pairs.append({"proposed_name": normalized_key, "raw_value": cleaned_value})

    return pairs
