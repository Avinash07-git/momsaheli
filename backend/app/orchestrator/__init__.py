"""AgentField-style orchestrator.

Phase 1: pure Python coroutines emitting SSE events. The shape mirrors what we'd
write with AgentField decorators in Phase 2 (`@app.reasoner`, `app.call`, etc.),
so the upgrade path is a search-and-replace, not a rewrite.
"""
from .runner import ACTIVATION_PLANS, EVENT_BUS, SwarmRunner

__all__ = ["SwarmRunner", "EVENT_BUS", "ACTIVATION_PLANS"]
