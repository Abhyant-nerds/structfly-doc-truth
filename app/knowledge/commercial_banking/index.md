---
okf_version: "0.1"
---

# Commercial Banking Knowledge Bundle

This bundle contains operational classification knowledge for commercial banking customer emails. It is consumed by the local email classification pipeline to retrieve focused category guidance before final classification.

# Contents

* [Issue Catalog](issue_catalog.md) - Business-domain grouping of supported operational categories.
* [Categories](categories/) - Category-level concepts with definitions, examples, routing boundaries, and evidence expectations.
* [Update Log](log.md) - Chronological history of knowledge bundle changes.

# Consumers

* `app/classification/okf_loader.py` - Loads category concepts from markdown frontmatter and bodies.
* `app/classification/retrieval.py` - Retrieves candidate categories using email text, routing summaries, and category metadata.
* `app/classification/pipeline.py` - Uses retrieved knowledge for final classification and validation.

