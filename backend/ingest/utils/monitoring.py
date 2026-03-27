"""Health monitoring helpers for the ingest pipeline."""

from __future__ import annotations

import logging

from sqlalchemy import func
from sqlalchemy.orm import Session

from ..models import IngestRun, Source

logger = logging.getLogger(__name__)


def check_consecutive_failures(
    session: Session,
    source_name: str,
    threshold: int = 3,
) -> bool:
    """Check if the last *threshold* runs for a source all failed.

    Returns ``True`` when an alert is warranted (all recent runs failed).
    """
    source = session.query(Source).filter_by(name=source_name).first()
    if source is None:
        return False

    recent_runs = (
        session.query(IngestRun)
        .filter_by(source_id=source.id)
        .order_by(IngestRun.started_at.desc())
        .limit(threshold)
        .all()
    )

    if len(recent_runs) < threshold:
        return False

    all_failed = all(r.status == "failed" for r in recent_runs)
    if all_failed:
        logger.warning(
            "ALERT: %s has %d consecutive failures",
            source_name,
            threshold,
        )
    return all_failed


def get_health_summary(session: Session) -> list[dict]:
    """Return health status for every registered source.

    Each entry contains:
    - name
    - last_run_status  (success / failed / never)
    - last_run_time    (ISO string or None)
    - consecutive_failures
    - total_runs
    """
    sources = session.query(Source).order_by(Source.name).all()

    # Batch-fetch all runs grouped by source_id to avoid N+1 queries
    source_ids = [src.id for src in sources]
    all_runs = (
        session.query(IngestRun)
        .filter(IngestRun.source_id.in_(source_ids))
        .order_by(IngestRun.source_id, IngestRun.started_at.desc())
        .all()
    )

    runs_by_source: dict[str, list[IngestRun]] = {}
    for run in all_runs:
        runs_by_source.setdefault(run.source_id, []).append(run)

    results: list[dict] = []

    for src in sources:
        runs = runs_by_source.get(src.id, [])
        total_runs = len(runs)

        if not runs:
            results.append(
                {
                    "name": src.name,
                    "last_run_status": "never",
                    "last_run_time": None,
                    "consecutive_failures": 0,
                    "total_runs": 0,
                }
            )
            continue

        last_run = runs[0]
        consecutive_failures = 0
        for r in runs:
            if r.status == "failed":
                consecutive_failures += 1
            else:
                break

        results.append(
            {
                "name": src.name,
                "last_run_status": last_run.status,
                "last_run_time": (
                    last_run.started_at.isoformat() if last_run.started_at else None
                ),
                "consecutive_failures": consecutive_failures,
                "total_runs": total_runs,
            }
        )

    return results
