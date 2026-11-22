"""`lab dataset ...` commands."""

from pathlib import Path
from typing import Annotated

import typer

from agentlab.async_runner import run_async
from agentlab.cli.console import console
from agentlab.cli.friendly_errors import friendly_errors
from agentlab.config.settings import get_settings
from agentlab.datasets.dataset_import_result import DatasetImportResult
from agentlab.datasets.dataset_importer import DatasetImporter
from agentlab.datasets.dataset_loader import DatasetLoader
from agentlab.db.database import Database
from agentlab.registry import DOMAINS

dataset_app = typer.Typer(help="Dataset commands.", no_args_is_help=True)


@dataset_app.command("import")
def import_dataset(
    path: Annotated[
        Path,
        typer.Argument(
            help="Dataset folder, e.g. datasets/support/v1.",
            exists=True,
            file_okay=False,
        ),
    ],
) -> None:
    """Validate a dataset folder and store it as an immutable version."""
    with friendly_errors():
        result = run_async(_import(path))
    label = f"{result.dataset_name} v{result.version}"
    details = f"{result.task_count} task(s), hash {result.content_hash[:12]}"
    if result.created:
        console.print(f"[green]Imported[/green] {label}: {details}")
    else:
        console.print(f"Already imported, unchanged: {label} ({details})")


async def _import(path: Path) -> DatasetImportResult:
    """Run the import against the main database."""
    database = Database(get_settings().database_url.get_secret_value())
    try:
        importer = DatasetImporter(database.sessions, DatasetLoader(DOMAINS))
        return await importer.import_path(path)
    finally:
        await database.dispose()
