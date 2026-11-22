"""Composition root: the only platform module that imports domain packs and agents.

Platform code receives these through parameters (`DOMAINS`, `build_agent`), so a new
domain or agent is added here without changing the platform.
"""

from collections.abc import Mapping
from typing import Any

from agentlab.agents.scripted_agent import ScriptedAgent
from agentlab.content_hash import content_hash
from agentlab.contracts.agent_adapter import AgentAdapter
from agentlab.contracts.domain_pack import DomainPack
from agentlab.domains.support.support_domain import SupportDomain
from agentlab.errors.agentlab_error import AgentlabError

DOMAINS: dict[str, DomainPack] = {SupportDomain.name: SupportDomain()}


def parse_agent_spec(spec: str, domain: DomainPack) -> tuple[str, dict[str, Any]]:
    """Turn a CLI agent spec such as `scripted:correct_refund` into adapter settings.

    The settings include a hash of the script content, so an edited script becomes
    a new, separately stored agent config.
    """
    adapter, _, value = spec.partition(":")
    if adapter == "scripted" and value:
        agent = ScriptedAgent.from_file(domain.scripts_dir / f"{value}.yaml")
        script = agent.script.model_dump(mode="json")
        return adapter, {"script": value, "script_hash": content_hash(script)}
    raise AgentlabError(f"Unknown agent spec '{spec}'. Use scripted:<script_name>.")


def build_agent(
    adapter: str, settings: Mapping[str, Any], domain: DomainPack
) -> AgentAdapter:
    """Build the agent described by a stored agent config."""
    if adapter == "scripted":
        agent = ScriptedAgent.from_file(
            domain.scripts_dir / f"{settings['script']}.yaml"
        )
        if (
            content_hash(agent.script.model_dump(mode="json"))
            != settings["script_hash"]
        ):
            raise AgentlabError(
                f"Script '{settings['script']}' changed after this agent config was "
                "stored. Configs are immutable: run it again to store a new config."
            )
        return agent
    raise AgentlabError(f"Unknown agent adapter '{adapter}'.")
