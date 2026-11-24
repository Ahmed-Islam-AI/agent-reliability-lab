"""A tool-calling agent written as an explicit LangGraph state graph."""

import json
from string import Template
from typing import Any

from langgraph.errors import GraphRecursionError
from langgraph.graph import END, START, StateGraph

from agentlab.agents.agent_state import AgentState
from agentlab.gateway.tool_gateway import ToolGateway
from agentlab.llm.model_gateway import ModelGateway
from agentlab.models.agent_input import AgentInput
from agentlab.models.agent_result import AgentResult
from agentlab.models.model_settings import ModelSettings
from agentlab.models.stop_reason import StopReason

# Backstop only: the model gateway's turn limit stops the agent long before this.
_RECURSION_LIMIT = 100


class LangGraphAgent:
    """START -> agent -> (tool calls? -> tools -> agent) | END.

    The agent node asks the model (through the model gateway) for the next step.
    The tools node runs the requested calls one after another (through the tool
    gateway) and returns their outputs to the model.
    """

    def __init__(self, settings: ModelSettings, system_prompt: str) -> None:
        self._settings = settings
        self._system_prompt = Template(system_prompt)

    async def run(
        self, agent_input: AgentInput, tools: ToolGateway, model: ModelGateway
    ) -> AgentResult:
        """Run the graph until the model answers without calling tools."""
        schemas = tools.visible_schemas()

        async def agent_node(state: AgentState) -> dict[str, Any]:
            response = await model.complete(state["messages"], schemas, self._settings)
            return {
                "messages": [response.message],
                "pending_tool_calls": response.tool_calls,
            }

        async def tools_node(state: AgentState) -> dict[str, Any]:
            results = []
            for call in state["pending_tool_calls"]:
                output = await tools.execute(call.name, call.arguments, call.id)
                results.append(
                    {
                        "role": "tool",
                        "tool_call_id": call.id,
                        "content": json.dumps(output),
                    }
                )
            return {"messages": results, "pending_tool_calls": []}

        def next_step(state: AgentState) -> str:
            return "tools" if state["pending_tool_calls"] else END

        graph = StateGraph(AgentState)
        graph.add_node("agent", agent_node)
        graph.add_node("tools", tools_node)
        graph.add_edge(START, "agent")
        graph.add_conditional_edges("agent", next_step, ["tools", END])
        graph.add_edge("tools", "agent")

        initial: AgentState = {
            "messages": self._opening_messages(agent_input),
            "pending_tool_calls": [],
        }
        try:
            final = await graph.compile().ainvoke(
                initial, config={"recursion_limit": _RECURSION_LIMIT}
            )
        except GraphRecursionError:
            return AgentResult(final_response="", stop_reason=StopReason.MAX_TURNS)
        return AgentResult(
            final_response=final["messages"][-1].get("content") or "",
            stop_reason=StopReason.FINAL_ANSWER,
        )

    def _opening_messages(self, agent_input: AgentInput) -> list[dict[str, Any]]:
        """System prompt (with today's date and the signed-in user) and user message."""
        today = agent_input.today.isoformat() if agent_input.today else "unknown"
        system = self._system_prompt.safe_substitute(
            today=today, user_id=agent_input.authenticated_user_id
        )
        return [
            {"role": "system", "content": system},
            {"role": "user", "content": agent_input.user_message},
        ]
