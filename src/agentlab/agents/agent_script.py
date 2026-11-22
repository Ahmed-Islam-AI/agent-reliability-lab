"""A scripted agent's full behavior, loaded from YAML."""

from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field

from agentlab.agents.script_step import ScriptStep


class AgentScript(BaseModel):
    """Tool calls to make in order, then the final reply to give."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    description: Annotated[str, Field(min_length=1)]
    steps: list[ScriptStep] = []
    final_response: Annotated[str, Field(min_length=1)]
