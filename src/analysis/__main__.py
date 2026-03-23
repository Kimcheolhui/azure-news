"""CLI entry point for the analysis pipeline."""

from __future__ import annotations

import logging
import sys

import click

logger = logging.getLogger("analysis")


@click.group()
@click.option("-v", "--verbose", is_flag=True, help="Enable debug logging.")
def cli(verbose: bool):
    """Azure Updates analysis pipeline."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
        level=level,
        stream=sys.stderr,
    )


@cli.group()
def generate():
    """Generate analysis reports."""


@generate.command("update")
@click.argument("update_id")
def generate_update(update_id: str):
    """Generate a report for a single update by ID."""
    click.echo(f"Generating report for update {update_id}...")
    # TODO: call pipeline orchestrator
    click.echo("Not yet implemented.")


@generate.command("pending")
def generate_pending():
    """Generate reports for all updates without reports."""
    from ingest.db.session import get_session
    from ingest.models import Update

    from .models import Report

    with get_session() as session:
        existing_ids = {
            r.update_id for r in session.query(Report.update_id).all()
        }
        pending = (
            session.query(Update)
            .filter(~Update.id.in_(existing_ids))
            .all()
        )
        click.echo(f"Found {len(pending)} updates without reports.")
        # TODO: call pipeline orchestrator for each
        click.echo("Not yet implemented.")


@generate.command("all")
def generate_all():
    """Regenerate reports for all updates."""
    click.echo("Regenerating all reports...")
    # TODO: call pipeline orchestrator for all
    click.echo("Not yet implemented.")


@cli.command()
def status():
    """Show report generation status."""
    from sqlalchemy import func as sqlfunc

    from ingest.db.session import get_session

    from .models import Report

    with get_session() as session:
        total = session.query(Report).count()
        if total == 0:
            click.echo("No reports generated yet.")
            return

        status_counts = (
            session.query(Report.status, sqlfunc.count(Report.id))
            .group_by(Report.status)
            .all()
        )

        click.echo(f"Total reports: {total}")
        click.echo("─" * 30)
        for s, count in sorted(status_counts, key=lambda x: x[0]):
            click.echo(f"  {s:<15} {count:>5}")


if __name__ == "__main__":
    cli()
