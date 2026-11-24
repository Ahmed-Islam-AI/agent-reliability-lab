"""A deterministic agent that replays a script. No model, no API key."""

from pathlib import Path
from typing import Any

import yaml
from pydantic import ValidationError

from agentlab.agents.agent_script import AgentScript
from agentlab.errors.agentlab_error import AgentlabError
from agentlab.errors.not_found_error import NotFoundError
from agentlab.gateway.tool_gateway import ToolGateway
from agentlab.llm.model_gateway import ModelGateway
from agentlab.models.agent_input import AgentInput
from agentlab.models.agent_result import AgentResult
from agentlab.models.stop_reason import StopReason


class ScriptedAgent:
    """Replays a fixed list of tool calls through the gateway, then replies.

    Used to test the platform for free and to produce known-good and known-bad
    behavior on purpose (wrong amount, missing approval, false success claim).
    """

    def __init__(self, script: AgentScript) -> None:
        self.script = script

    @classmethod
    def from_file(cls, path: Path) -> "ScriptedAgent":
        """Load a script from a YAML file."""
        if not path.is_file():
            raise NotFoundError(f"Agent script not found: {path}")
        try:
            script = AgentScript.model_validate(yaml.safe_load(path.read_text("utf-8")))
        except (yaml.YAMLError, ValidationError) as exc:
            raise AgentlabError(f"Invalid agent script {path}: {exc}") from exc
        return cls(script)

    async def run(
        self, agent_input: AgentInput, tools: ToolGateway, model: ModelGateway
    ) -> AgentResult:
        """Run every scripted tool call in order and return the scripted reply.

        The model gateway is not used: a scripted agent never calls a model.
        """
        outputs: dict[str, Any] = {}
        for index, step in enumerate(self.script.steps, start=1):
            arguments = {
                key: _resolve(value, outputs) for key, value in step.args.items()
            }
            output = await tools.execute(step.tool, arguments, call_id=f"call_{index}")
            outputs.update(output)
        return AgentResult(
            final_response=self.script.final_response,
            stop_reason=StopReason.FINAL_ANSWER,
            metadata={"script": self.script.name},
        )


def _resolve(value: Any, outputs: dict[str, Any]) -> Any:
    """Replace a `$name` placeholder with the latest output value called `name`."""
    if isinstance(value, str) and value.startswith("$"):
        return outputs.get(value[1:], value)
    return value
