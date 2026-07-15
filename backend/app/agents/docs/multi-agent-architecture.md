# Multi-Agent Architecture

The agent platform separates registry, runtime, scheduling, orchestration, communication, memory, security, governance, and monitoring concerns into dedicated backend components.

Agents are registered in the agent registry, executed through the runtime manager, routed through the orchestrator, and monitored through snapshot metrics. Redis-backed queues and caches can be added without changing the API contract because the service layer depends on the runtime abstractions rather than a concrete transport.
