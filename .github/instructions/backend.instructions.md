---
applyTo: "backend/**/*.py"
---

# Python Backend Conventions

## File Header

Every `.py` file must start with:

```python
from __future__ import annotations
```

## Config Pattern

Use `@dataclass(frozen=True)` with a `from_env()` classmethod. See `backend/ingest/config.py` as reference.

## Models

- SQLAlchemy 2.0 declarative style (mapped_column, Mapped types)
- UUID primary keys
- JSONB for flexible fields
- Models in `backend/ingest/models/` (shared by all modules)
- Analysis-specific models in `backend/analysis/models/`

## Testing

- Test file per module: `backend/tests/test_<module>.py`
- Shared fixtures in `backend/tests/conftest.py`
- Use `MagicMock` for DB objects, no real DB in tests
- Run: `cd backend && pytest tests/ --tb=short -q`

## Scrapers

- Extend `BaseScraper` from `backend/ingest/scrapers/base.py`
- One file per source in `backend/ingest/scrapers/`
- Register in `backend/ingest/scrapers/__init__.py` SCRAPERS dict

## Analysis Pipeline

- Prompt templates: YAML files in `backend/analysis/prompts/*.yml`
- Pipeline: researcher → analyzer → enrichment → writer
- Orchestrator in `backend/analysis/pipeline/orchestrator.py`

## CLI

- Ingest CLI: `python -m ingest <command>` (Click)
- Analysis CLI: `python -m analysis <command>` (Click)
- API server: `uvicorn api.app:app --reload`

## Dependencies

- All deps in `backend/pyproject.toml`
- Install: `pip install -e ".[dev]"`
