# Microsoft News — Project Instructions

Azure 에코시스템 업데이트를 수집·분석·표시하는 풀스택 서비스. Python 백엔드 + SvelteKit 프론트엔드 모노레포.

## Architecture

```
backend/
  ingest/     ← 스크래핑 파이프라인 (Click CLI, SQLAlchemy, BeautifulSoup)
  analysis/   ← LLM 분석 파이프라인 (OpenAI API, 리포트 생성)
  api/        ← REST API (FastAPI, uvicorn)
  tests/      ← pytest 테스트 전체
frontend/     ← SvelteKit 5 + Tailwind CSS 4 + TypeScript
```

## Tech Stack

| Layer           | Stack                                             |
| --------------- | ------------------------------------------------- |
| Backend runtime | Python 3.11+                                      |
| DB              | PostgreSQL, SQLAlchemy 2.0, Alembic               |
| Scraping        | requests, BeautifulSoup4, feedparser              |
| LLM             | OpenAI API (or Azure OpenAI), gpt-5.4-mini        |
| API             | FastAPI, uvicorn                                  |
| CLI             | Click                                             |
| Frontend        | SvelteKit 5 (Svelte 5 runes mode), Tailwind CSS 4 |
| Tests           | pytest, pytest-asyncio, httpx                     |

## Build & Run

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# Ingest
python -m ingest sources seed
python -m ingest scrape run --all

# Analysis
python -m analysis generate update --all

# API
uvicorn api.app:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Tests

```bash
cd backend
pytest tests/ --tb=short -q
```

Always run tests after modifying backend code.

## Code Conventions

### Python

- `from __future__ import annotations` at the top of every file
- Config via `@dataclass(frozen=True)` + `from_env()` classmethod, env vars loaded with `python-dotenv`
- snake_case for all identifiers
- Type hints everywhere
- Tests in `backend/tests/`, filenames: `test_<module>.py`
- Fixtures in `conftest.py`

### Frontend (Svelte)

- Svelte 5 runes mode (`$state`, `$derived`, `$effect` — NOT `let` reactive declarations)
- Tailwind CSS 4 for styling (no separate CSS files except layout.css)
- API calls in `src/lib/api/client.ts`
- Reusable components in `src/lib/components/`
- Routes: `src/routes/` (SvelteKit file-based routing)

### Database

- Models in `backend/ingest/models/` (SQLAlchemy declarative base)
- Migrations via Alembic (`backend/ingest/db/migrations/`)
- Session factory in `backend/ingest/db/session.py`
- UUID primary keys
- JSONB columns for flexible fields (categories, affected_services)

## Key Patterns

- **Scrapers** extend `BaseScraper` in `backend/ingest/scrapers/base.py`. Each source has its own file.
- **Prompts** are stored as YAML files in `backend/analysis/prompts/*.yml`, loaded by `loader.py`.
- **Pipeline stages**: researcher → analyzer → enrichment → writer (orchestrated by `orchestrator.py`)
- **Dedup** logic in `backend/ingest/utils/dedup.py` (URL-based matching)
- **Retry** with exponential backoff in `backend/ingest/utils/retry.py`

## CI/CD

- `.github/workflows/test.yml` — pytest on push/PR to main
- `.github/workflows/ingest-schedule.yml` — scheduled scraping (06:00, 18:00 UTC)
- `.github/workflows/ingest-manual.yml` — manual trigger with source selection

## Language

- Code, git commits, comments: English
- UI labels, user-facing text: Primarily English (some Korean in tooltips/descriptions)
- BACKLOG.md: Korean
- Communication with the developer: Korean is preferred
