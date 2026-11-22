"""One tool call in a scripted agent's script."""

from typing import Annotated, Any

from pydantic import BaseModel, ConfigDict, Field


class ScriptStep(BaseModel):
    """A tool name and its arguments.

    A string argument of the form `$name` is replaced with the value of `name` from
    the most recent tool output that contains it (for example `$approval_id`).
    """

    model_config = ConfigDict(extra="forbid", frozen=True)

    tool: Annotated[str, Field(min_length=1)]
    args: dict[str, Any] = {}
