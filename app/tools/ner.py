import re


ORG_SUFFIXES = ("inc", "llc", "ltd", "limited", "corp", "corporation", "pvt")


def extract_named_entities(text):
    if not isinstance(text, str):
        return []

    matches = re.findall(r"\b[A-Z][A-Za-z0-9&.,-]*(?:\s+[A-Z][A-Za-z0-9&.,-]*)*\b", text)
    entities = []
    seen = set()

    for match in matches:
        cleaned_match = match.strip(" ,.")
        if len(cleaned_match) < 3:
            continue

        proposed_name = "organization"
        if not any(cleaned_match.lower().endswith(suffix) for suffix in ORG_SUFFIXES):
            proposed_name = "named_entity"

        key = (proposed_name, cleaned_match.lower())
        if key in seen:
            continue

        seen.add(key)
        entities.append({"proposed_name": proposed_name, "raw_value": cleaned_match})

    return entities
