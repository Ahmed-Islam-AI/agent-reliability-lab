"""State carried between the nodes of the LangGraph agent."""

import operator
from typing import Annotated, Any, TypedDict

from agentlab.models.llm_tool_call import LlmToolCall


class AgentState(TypedDict):
    """Conversation so far and the tool calls waiting to run.

    `messages` uses an append reducer: each node returns only its new messages.
    """

    messages: Annotated[list[dict[str, Any]], operator.add]
    pending_tool_calls: list[LlmToolCall]
