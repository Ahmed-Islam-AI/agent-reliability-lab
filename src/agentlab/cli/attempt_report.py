"""Print a stored attempt: statuses, trace and scores, read back from the database."""

import json
from typing import Any
from uuid import UUID

from rich.markup import escape
from rich.panel import Panel
from rich.table import Table
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from agentlab.cli.console import console
from agentlab.db.tables.agent_config_table import AgentConfigTable
from agentlab.db.tables.attempt_table import AttemptTable
from agentlab.db.tables.run_table import RunTable
from agentlab.db.tables.score_table import ScoreTable
from agentlab.db.tables.task_version_table import TaskVersionTable
from agentlab.db.tables.trace_event_table import TraceEventTable
from agentlab.errors.not_found_error import NotFoundError
from agentlab.models.event_type import EventType

_COLORS = {"pass": "green", "ok": "green", "fail": "red", "denied": "red"}


async def print_attempt(
    sessions: async_sessionmaker[AsyncSession], attempt_id: UUID
) -> None:
    """Load the attempt from the database and render it."""
    async with sessions() as session:
        attempt = await session.get(AttemptTable, attempt_id)
        if attempt is None:
            raise NotFoundError(f"Attempt {attempt_id} not found.")
        task_id, agent_name = (
            await session.execute(
                select(TaskVersionTable.task_id, AgentConfigTable.name)
                .select_from(RunTable)
                .join(TaskVersionTable, RunTable.task_version_id == TaskVersionTable.id)
                .join(AgentConfigTable, RunTable.agent_config_id == AgentConfigTable.id)
                .where(RunTable.id == attempt.run_id)
            )
        ).one()
        events = (
            await session.scalars(
                select(TraceEventTable)
                .where(TraceEventTable.attempt_id == attempt_id)
                .order_by(TraceEventTable.sequence)
            )
        ).all()
        scores = (
            await session.scalars(
                select(ScoreTable)
                .where(ScoreTable.attempt_id == attempt_id)
                .order_by(ScoreTable.id)
            )
        ).all()

    console.print(
        Panel(
            f"task [bold]{task_id}[/bold]   agent [bold]{escape(agent_name)}[/bold]\n"
            f"execution {_colored(attempt.execution_status)}   "
            f"evaluation {_colored(attempt.evaluation_status)}   "
            f"stop reason {attempt.stop_reason or '-'}\n"
            f"attempt {attempt.id}",
            title="Attempt",
        )
    )
    trace = Table(title="Trace", show_lines=False)
    for column in ("#", "event", "status", "detail"):
        trace.add_column(column)
    for event in events:
        trace.add_row(
            str(event.sequence),
            event.event_type,
            _colored(event.status or ""),
            escape(_detail(event.event_type, event.payload)),
        )
    console.print(trace)

    table = Table(title="Scores")
    for column in ("evaluator", "dimension", "status", "reason", "evidence"):
        table.add_column(column)
    for score in scores:
        table.add_row(
            score.evaluator,
            score.dimension,
            _colored(score.status),
            score.reason_code or "-",
            escape(_short(score.evidence, 160)),
        )
    console.print(table)
    console.print(
        f"[bold]Final response:[/bold] {escape(attempt.final_response or '-')}"
    )


def _detail(event_type: str, payload: dict[str, Any]) -> str:
    """Summarize an event payload in one line."""
    if event_type == EventType.TOOL_REQUESTED:
        return f"{payload['tool']}({_short(payload['arguments'], 90)})"
    if event_type in (EventType.TOOL_FINISHED, EventType.TOOL_REJECTED):
        return _short(payload["output"], 110)
    if event_type == EventType.AGENT_FINISHED:
        return _short(payload.get("final_response", ""), 110)
    if event_type == EventType.EVALUATOR_FINISHED:
        return str(payload.get("evaluator", ""))
    return _short(payload, 110) if payload else ""


def _short(value: Any, limit: int) -> str:
    """Return compact JSON (or text) cut to `limit` characters."""
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False)
    return text if len(text) <= limit else text[: limit - 1] + "…"


def _colored(status: str) -> str:
    """Wrap a status in a Rich color tag."""
    color = _COLORS.get(status, "yellow")
    return f"[{color}]{status}[/{color}]" if status else ""
