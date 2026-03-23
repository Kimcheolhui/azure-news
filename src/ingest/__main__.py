"""CLI entry point for the ingest pipeline."""

import click


@click.group()
def cli():
    """Azure Updates ingestion pipeline."""


@cli.group()
def scrape():
    """Run scrapers to ingest updates."""


@scrape.command("run")
@click.option("--source", default=None, help="Scrape a specific source by name.")
@click.option("--all", "all_sources", is_flag=True, help="Scrape all enabled sources.")
def scrape_run(source: str | None, all_sources: bool):
    """Scrape updates from one or all sources."""
    if source:
        click.echo(f"Scraping source '{source}' — not implemented yet.")
    elif all_sources:
        click.echo("Scraping all sources — not implemented yet.")
    else:
        click.echo("Specify --source <name> or --all.")


@cli.group()
def sources():
    """Manage ingest sources."""


@sources.command("list")
def sources_list():
    """List configured sources."""
    click.echo("Not implemented yet.")


@cli.command()
@click.option("--last", "last_n", default=10, help="Number of recent runs to show.")
def runs(last_n: int):
    """Show recent ingest runs."""
    click.echo(f"Showing last {last_n} runs — not implemented yet.")


if __name__ == "__main__":
    cli()
