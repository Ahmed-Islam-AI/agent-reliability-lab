"""Turn expected failures into short CLI messages instead of tracebacks."""

from collections.abc import Iterator
from contextlib import contextmanager

import typer
from rich.markup import escape
from sqlalchemy.exc import OperationalError

from agentlab.cli.console import console
from agentlab.errors.agentlab_error import AgentlabError

_DATABASE_DOWN = (
    "Cannot reach the database. Start it with `docker compose up -d postgres`, "
    "then run `uv run lab db migrate`."
)


@contextmanager
def friendly_errors() -> Iterator[None]:
    """Print expected errors in one red line and exit with status 1."""
    try:
        yield
    except AgentlabError as exc:
        console.print(f"[red]Error:[/red] {escape(str(exc))}")
        raise typer.Exit(1) from exc
    except OperationalError as exc:
        console.print(f"[red]Error:[/red] {_DATABASE_DOWN}")
        raise typer.Exit(1) from exc
