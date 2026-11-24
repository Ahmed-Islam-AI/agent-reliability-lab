"""`lab run-task`: run one attempt of one task inline."""

from pathlib import Path
from typing import Annotated

import typer

from agentlab.async_runner import run_async
from agentlab.cli.attempt_report import print_attempt
from agentlab.cli.friendly_errors import friendly_errors
from agentlab.config.settings import get_settings
from agentlab.db.database import Database
from agentlab.errors.agentlab_error import AgentlabError
from agentlab.execution.adhoc_run import (
    create_adhoc_run,
    dataset_domain,
    finish_adhoc_run,
)
from agentlab.execution.attempt_executor import AttemptExecutor
from agentlab.execution.attempt_runner import AttemptRunner
from agentlab.llm.lite_llm_client import LiteLlmClient
from agentlab.registry import DOMAINS, build_agent, load_agent_config, parse_agent_spec


def run_task(
    task_id: Annotated[str, typer.Argument(help="Task id, e.g. refund_eligible_001.")],
    agent: Annotated[
        str | None,
        typer.Option("--agent", help="Scripted agent, e.g. scripted:correct_refund."),
    ] = None,
    agent_config: Annotated[
        Path | None,
        typer.Option(
            "--agent-config",
            help="Agent config file, e.g. agent_configs/support_groq_a_v1.yaml.",
            exists=True,
            dir_okay=False,
        ),
    ] = None,
    dataset: Annotated[
        str, typer.Option("--dataset", help="Dataset name (latest version is used).")
    ] = "support",
) -> None:
    """Run one attempt of a task and print its trace, model calls and scores."""
    with friendly_errors():
        if (agent is None) == (agent_config is None):
            raise AgentlabError("Pass exactly one of --agent or --agent-config.")
        run_async(_run_task(task_id, agent, agent_config, dataset))


async def _run_task(
    task_id: str, agent: str | None, agent_config: Path | None, dataset: str
) -> None:
    """Create a one-run experiment, execute it and print the stored result."""
    settings = get_settings()
    database = Database(settings.database_url.get_secret_value())
    try:
        domain_name = await dataset_domain(database.sessions, dataset)
        domain = DOMAINS.get(domain_name)
        if domain is None:
            raise AgentlabError(f"No domain pack registered for '{domain_name}'.")
        if agent_config is not None:
            spec = load_agent_config(agent_config, domain, settings.config_variables())
        elif agent is not None:
            spec = parse_agent_spec(agent, domain)
        else:
            raise AgentlabError("Pass exactly one of --agent or --agent-config.")
        run_id = await create_adhoc_run(
            database.sessions, dataset_name=dataset, task_id=task_id, agent=spec
        )
        executor = AttemptExecutor(
            LiteLlmClient(settings.api_keys()), settings.llm_max_retries
        )
        runner = AttemptRunner(database.sessions, DOMAINS, build_agent, executor)
        attempt_id = await runner.run(run_id, settings.platform_limits())
        await finish_adhoc_run(database.sessions, run_id)
        await print_attempt(database.sessions, attempt_id)
    finally:
        await database.dispose()
