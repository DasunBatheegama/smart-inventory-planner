from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from app.agents.base import BaseAgent


class AgentRegistrationError(Exception):
    """Raised when an agent cannot be registered."""


class AgentNotFoundError(Exception):
    """Raised when a requested agent is not registered."""


class AgentRegistry:
    """Foundation registry for AI agents.

    Future agents (Forecast Agent, Inventory Agent, Insight Agent, AI
    Orchestrator) can register here and be invoked through a common entry
    point. No concrete agents are registered in this stage.
    """

    def __init__(self) -> None:
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        from app.agents.base import BaseAgent

        if not isinstance(agent, BaseAgent):
            raise AgentRegistrationError("Only BaseAgent instances can be registered.")
        if agent.name in self._agents:
            raise AgentRegistrationError(f"Agent '{agent.name}' is already registered.")
        self._agents[agent.name] = agent

    def get(self, name: str) -> BaseAgent:
        if name not in self._agents:
            raise AgentNotFoundError(f"Agent '{name}' is not registered.")
        return self._agents[name]

    def run(self, name: str, user_message: str) -> str:
        return self.get(name).invoke(user_message)

    def registered_names(self) -> list[str]:
        return sorted(self._agents)


agent_registry = AgentRegistry()


def run_agent(name: str, user_message: str) -> str:
    return agent_registry.run(name, user_message)