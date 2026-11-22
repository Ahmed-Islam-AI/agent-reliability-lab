"""`lab db ...` commands."""

from pathlib import Path

import typer
from alembic import command
from alembic.config import Config

from agentlab.cli.console import console
from agentlab.cli.friendly_errors import friendly_errors
from agentlab.config.settings import get_settings
from agentlab.errors.agentlab_error import AgentlabError

db_app = typer.Typer(help="Database commands.", no_args_is_help=True)


@db_app.command("migrate")
def migrate() -> None:
    """Apply every pending migration to the main database."""
    with friendly_errors():
        ini = Path("alembic.ini")
        if not ini.is_file():
            raise AgentlabError(
                "alembic.ini not found. Run lab from the repository root."
            )
        config = Config(str(ini))
        config.attributes["database_url"] = (
            get_settings().database_url.get_secret_value()
        )
        command.upgrade(config, "head")
    console.print("[green]Database is up to date.[/green]")
