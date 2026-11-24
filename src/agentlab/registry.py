"""Composition root: the only platform module that imports domain packs and agents.

Platform code receives these through parameters (`DOMAINS`, `build_agent`), so a new
domain or agent is added here without changing the platform.
"""

from collections.abc import Mapping
from pathlib import Path
from typing import Any

from agentlab.agents.agent_config_file import AgentConfigFile
from agentlab.agents.langgraph_agent import LangGraphAgent
from agentlab.agents.scripted_agent import ScriptedAgent
from agentlab.content_hash import content_hash
from agentlab.contracts.agent_adapter import AgentAdapter
from agentlab.contracts.domain_pack import DomainPack
from agentlab.domains.support.support_domain import SupportDomain
from agentlab.errors.agentlab_error import AgentlabError
from agentlab.errors.not_found_error import NotFoundError
from agentlab.models.agent_config_spec import AgentConfigSpec
from agentlab.models.model_settings import ModelSettings

DOMAINS: dict[str, DomainPack] = {SupportDomain.name: SupportDomain()}


def parse_agent_spec(spec: str, domain: DomainPack) -> AgentConfigSpec:
    """Turn a CLI agent spec such as `scripted:correct_refund` into a config.

    The settings include a hash of the script content, so an edited script becomes
    a new, separately stored agent config.
    """
    adapter, _, value = spec.partition(":")
    if adapter == "scripted" and value:
        agent = ScriptedAgent.from_file(domain.scripts_dir / f"{value}.yaml")
        script = agent.script.model_dump(mode="json")
        return AgentConfigSpec(
            name=spec,
            adapter=adapter,
            settings={"script": value, "script_hash": content_hash(script)},
        )
    raise AgentlabError(f"Unknown agent spec '{spec}'. Use scripted:<script_name>.")


def load_agent_config(
    path: Path, domain: DomainPack, variables: Mapping[str, str]
) -> AgentConfigSpec:
    """Read an agent config file and the prompt it names.

    The settings hold the resolved model id and the prompt's hash, so changing
    either produces a new, separately stored agent config.
    """
    config = AgentConfigFile.from_file(path, variables)
    prompt_text = _read_prompt(domain, config.prompt)
    return AgentConfigSpec(
        name=config.name,
        adapter=config.adapter,
        settings={
            "model": config.model,
            "temperature": config.temperature,
            "max_output_tokens": config.max_output_tokens,
            "prompt": config.prompt,
            "prompt_hash": content_hash(prompt_text),
        },
        prompt_name=config.prompt,
        prompt_text=prompt_text,
    )


def build_agent(
    adapter: str, settings: Mapping[str, Any], domain: DomainPack
) -> AgentAdapter:
    """Build the agent described by a stored agent config.

    Refuses to run if the script or prompt file changed after the config was
    stored, because the stored config would no longer describe what runs.
    """
    if adapter == "scripted":
        agent = ScriptedAgent.from_file(
            domain.scripts_dir / f"{settings['script']}.yaml"
        )
        _check_unchanged(
            f"Script '{settings['script']}'",
            content_hash(agent.script.model_dump(mode="json")),
            settings["script_hash"],
        )
        return agent
    if adapter == "langgraph":
        prompt_text = _read_prompt(domain, settings["prompt"])
        _check_unchanged(
            f"Prompt '{settings['prompt']}'",
            content_hash(prompt_text),
            settings["prompt_hash"],
        )
        model_settings = ModelSettings(
            model=settings["model"],
            temperature=settings["temperature"],
            max_output_tokens=settings["max_output_tokens"],
        )
        return LangGraphAgent(model_settings, prompt_text)
    raise AgentlabError(f"Unknown agent adapter '{adapter}'.")


def _read_prompt(domain: DomainPack, name: str) -> str:
    """Return the text of `<prompts_dir>/<name>.md`."""
    path = domain.prompts_dir / f"{name}.md"
    if not path.is_file():
        raise NotFoundError(f"Prompt not found: {path}")
    return path.read_text("utf-8")


def _check_unchanged(what: str, current: str, stored: str) -> None:
    """Raise if a file's content no longer matches the stored config."""
    if current != stored:
        raise AgentlabError(
            f"{what} changed after this agent config was stored. Configs are "
            "immutable: run it again to store a new config."
        )
