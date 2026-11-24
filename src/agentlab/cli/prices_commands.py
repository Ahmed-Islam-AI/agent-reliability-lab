"""`lab prices ...` commands."""

from datetime import UTC, datetime
from decimal import Decimal

import typer
from rich.table import Table

from agentlab.async_runner import run_async
from agentlab.cli.console import console
from agentlab.cli.friendly_errors import friendly_errors
from agentlab.config.settings import get_settings
from agentlab.db.database import Database
from agentlab.errors.agentlab_error import AgentlabError
from agentlab.llm.price_sync import sync_prices
from agentlab.llm.price_sync_result import PriceSyncResult

prices_app = typer.Typer(help="Model price commands.", no_args_is_help=True)

_STATUS_STYLE = {"added": "green", "unchanged": "dim", "missing": "red"}


@prices_app.command("sync")
def sync() -> None:
    """Store list prices of AGENT_MODEL_A and AGENT_MODEL_B from LiteLLM's map."""
    settings = get_settings()
    models = [
        model for model in (settings.agent_model_a, settings.agent_model_b) if model
    ]
    with friendly_errors():
        if not models:
            raise AgentlabError(
                "Set AGENT_MODEL_A (and optionally AGENT_MODEL_B) in .env."
            )
        results = run_async(_sync(models))
    table = Table(title="Model prices (USD per million tokens)")
    for column in ("model", "status", "input", "output"):
        table.add_column(column)
    for result in results:
        style = _STATUS_STYLE[result.status]
        table.add_row(
            result.model,
            f"[{style}]{result.status}[/{style}]",
            _usd(result.input_usd_per_million),
            _usd(result.output_usd_per_million),
        )
    console.print(table)
    if any(result.status == "missing" for result in results):
        console.print(
            "[red]Missing prices mean estimated cost will show as unknown.[/red]"
        )


def _usd(value: Decimal | None) -> str:
    """A rate without trailing zeros (0.15, not 0.15000000)."""
    return "-" if value is None else f"{value.normalize():f}"


async def _sync(models: list[str]) -> list[PriceSyncResult]:
    """Run the sync against the main database."""
    database = Database(get_settings().database_url.get_secret_value())
    try:
        return await sync_prices(database.sessions, models, datetime.now(UTC).date())
    finally:
        await database.dispose()
