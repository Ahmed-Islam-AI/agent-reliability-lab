"""The `lab` command line."""

import typer

from agentlab.cli.dataset_commands import dataset_app
from agentlab.cli.db_commands import db_app
from agentlab.cli.prices_commands import prices_app
from agentlab.cli.run_task_command import run_task
from agentlab.config.logging_config import configure_logging
from agentlab.config.settings import get_settings

# Locals are hidden in tracebacks so secrets from settings never reach the terminal.
app = typer.Typer(
    name="lab",
    help="Evaluate tool-using AI agents.",
    no_args_is_help=True,
    pretty_exceptions_show_locals=False,
)
app.add_typer(db_app, name="db")
app.add_typer(dataset_app, name="dataset")
app.add_typer(prices_app, name="prices")
app.command("run-task")(run_task)


@app.callback()
def main() -> None:
    """agent-reliability-lab: run, trace and score agents on versioned tasks."""
    configure_logging(get_settings().log_level)
