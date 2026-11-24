"""An agent configuration file (`agent_configs/*.yaml`)."""

from collections.abc import Mapping
from pathlib import Path
from string import Template
from typing import Annotated, Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

from agentlab.errors.agentlab_error import AgentlabError
from agentlab.errors.not_found_error import NotFoundError


class AgentConfigFile(BaseModel):
    """Which adapter, model, prompt and settings an agent uses."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    name: Annotated[str, Field(pattern=r"^[a-z0-9_]+$")]
    adapter: Literal["langgraph"]
    model: Annotated[
        str,
        Field(
            min_length=3, description="LiteLLM model id, e.g. groq/openai/gpt-oss-120b."
        ),
    ]
    temperature: Annotated[float, Field(ge=0.0, le=2.0)] = 0.0
    max_output_tokens: Annotated[int, Field(ge=16, le=65536)] = 1024
    prompt: Annotated[
        str,
        Field(
            pattern=r"^[a-z0-9_]+$",
            description="Prompt file (without .md) in the domain's prompts folder.",
        ),
    ]

    @classmethod
    def from_file(cls, path: Path, variables: Mapping[str, str]) -> "AgentConfigFile":
        """Load a config, replacing `${NAME}` with values such as `AGENT_MODEL_A`.

        The resolved value is what gets stored, so switching providers in `.env`
        produces a new, separately versioned agent config.
        """
        if not path.is_file():
            raise NotFoundError(f"Agent config not found: {path}")
        try:
            text = Template(path.read_text("utf-8")).substitute(variables)
        except KeyError as exc:
            raise AgentlabError(
                f"{path.name} uses ${{{exc.args[0]}}}, which is not set in .env."
            ) from exc
        try:
            return cls.model_validate(yaml.safe_load(text))
        except (yaml.YAMLError, ValidationError) as exc:
            raise AgentlabError(f"Invalid agent config {path}: {exc}") from exc
