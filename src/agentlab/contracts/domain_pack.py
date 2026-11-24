"""Contract every business domain implements to plug into the platform."""

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any, Protocol

from agentlab.contracts.environment import Environment
from agentlab.contracts.evaluator import Evaluator
from agentlab.models.task_definition import TaskDefinition
from agentlab.models.tool_spec import ToolSpec


class DomainPack(Protocol):
    """Environment, tools and evaluators for one business domain."""

    name: str
    scripts_dir: Path
    """Folder holding scripted-agent YAML scripts for this domain."""
    prompts_dir: Path
    """Folder holding system prompt files (`<name>.md`) for this domain."""

    def tools(self) -> Sequence[ToolSpec]:
        """Return every tool the agent may call in this domain."""
        ...

    def create_environment(
        self, fixture: Mapping[str, Any], scenario: Mapping[str, Any]
    ) -> Environment:
        """Build fresh state from a merged fixture and the task's scenario."""
        ...

    def validate_task(self, task: TaskDefinition, fixture: Mapping[str, Any]) -> None:
        """Raise `ValueError` if the task does not fit this domain."""
        ...

    def evaluators(self) -> Sequence[Evaluator]:
        """Return the domain's evaluators."""
        ...
