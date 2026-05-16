"""Swarm runner — wires the 5 agents and emits SSE events.

EVENT_BUS is a tiny pub/sub keyed by run_id. The FastAPI SSE endpoint subscribes
to a run_id and yields events as they arrive.

This is the AgentField-equivalent for Phase 1. In Phase 2 we swap to
`@app.reasoner` + `app.call()` so every cross-agent call gets the AgentField
audit trail, but the public shape of `SwarmRunner.run()` stays the same.
"""
from __future__ import annotations

import asyncio
import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime
from typing import Any, AsyncIterator

from app.adapters import butterbase, bright_data
from app.agents import (
    run_launch_agent,
    run_market_scout,
    run_memory_agent,
    run_profile_agent,
    run_reality_compliance,
)
from app.schemas import AgentEvent, RunSummary

log = logging.getLogger(__name__)


class _EventBus:
    """In-process pub/sub. One asyncio.Queue per run_id."""

    def __init__(self) -> None:
        self._queues: dict[str, asyncio.Queue[AgentEvent | None]] = defaultdict(asyncio.Queue)

    def queue_for(self, run_id: str) -> asyncio.Queue:
        return self._queues[run_id]

    async def publish(self, event: AgentEvent) -> None:
        await self._queues[event.run_id].put(event)

    async def close(self, run_id: str) -> None:
        # None signals end-of-stream
        await self._queues[run_id].put(None)

    async def stream(self, run_id: str) -> AsyncIterator[AgentEvent]:
        q = self.queue_for(run_id)
        while True:
            event = await q.get()
            if event is None:
                return
            yield event


EVENT_BUS = _EventBus()


class SwarmRunner:
    """One swarm execution. Wires the 5 agents, emits events, returns a run_id."""

    def __init__(self, raw_profile: dict[str, Any]):
        self.run_id = f"run_{uuid.uuid4().hex[:12]}"
        self.raw_profile = raw_profile
        self._start_time = 0.0

    async def _emit(self, type_: str, agent: str, data: dict[str, Any]) -> None:
        ev = AgentEvent(type=type_, agent=agent, run_id=self.run_id, data=data)
        await EVENT_BUS.publish(ev)

    async def run(self) -> None:
        """Fire the full swarm. Emits events along the way. Closes the stream when done."""
        self._start_time = time.time()
        try:
            await self._emit("run_started", "system", {"run_id": self.run_id})
            await asyncio.sleep(0.2)

            # --- 1. Profile Agent ---
            profile = await run_profile_agent(self.raw_profile)
            await self._emit("profile_ready", "profile", {"profile": profile.model_dump(mode="json")})
            await asyncio.sleep(0.3)

            # --- 2. Market Scout + parallel state-law prefetch ---
            # Kick off the (slower) state-law scrape in parallel with the (much slower)
            # Gemini-powered Market Scout ranking. Both depend only on the profile.
            law_prefetch_task: asyncio.Task | None = None
            if profile.state:
                law_prefetch_task = asyncio.create_task(
                    bright_data.scrape_state_law(profile.state)
                )

            cards, opportunities = await run_market_scout(profile)
            for c in cards:
                await self._emit("evidence_card", "market_scout", {"card": c.model_dump(mode="json")})
                await asyncio.sleep(0.15)  # tasty streaming feel
            await self._emit(
                "opportunities_ranked",
                "market_scout",
                {"opportunities": [o.model_dump(mode="json") for o in opportunities]},
            )
            await asyncio.sleep(0.3)

            # --- 3. Reality & Compliance ---
            # By the time we get here, the prefetch task has had ~16s of head-start.
            pre_law = await law_prefetch_task if law_prefetch_task else None
            checks = []
            winner = None
            rejected = []
            async for check in run_reality_compliance(opportunities, profile, pre_fetched_law=pre_law):
                checks.append(check)
                await self._emit("compliance_check", "reality_compliance", {"check": check.model_dump(mode="json")})
                await asyncio.sleep(0.4)  # dramatic pause for BLOCKs
                if check.verdict == "PASS" and winner is None:
                    winner = next((o for o in opportunities if o.id == check.opportunity_id), None)
                elif check.verdict == "BLOCK":
                    blocked = next((o for o in opportunities if o.id == check.opportunity_id), None)
                    if blocked:
                        rejected.append(blocked)

            if winner is None:
                # No opportunity passed — pick the best ranked anyway so the demo doesn't dead-end
                winner = opportunities[0] if opportunities else None

            if winner is None:
                await self._emit("agent_error", "reality_compliance", {"error": "no_winner"})
                await self._finish(profile_display="(unknown)", winner_offer="(none)", launch_url=None)
                return

            await self._emit("winner_selected", "reality_compliance", {"opportunity_id": winner.id})
            await asyncio.sleep(0.2)

            # --- 4. Launch Agent ---
            packet, launch_url = await run_launch_agent(winner, profile)
            await self._emit("launch_packet_ready", "launch", {"packet": packet.model_dump(mode="json")})
            await asyncio.sleep(0.2)
            await self._emit("launch_published", "launch", {"url": launch_url, "slug": launch_url.rsplit("/", 1)[-1]})
            await asyncio.sleep(0.2)

            # --- 5. Memory Agent ---
            _, pattern = await run_memory_agent(
                run_id=self.run_id,
                profile=profile,
                winner=winner,
                rejected=rejected,
                compliance_checks=checks,
            )
            if pattern:
                await self._emit("memory_pattern", "memory", {"pattern": pattern.model_dump(mode="json")})
            await asyncio.sleep(0.2)

            await self._finish(
                profile_display=profile.display_name,
                winner_offer=packet.offer_name,
                launch_url=launch_url,
            )

        except Exception as e:
            log.exception("swarm.failed")
            await self._emit("agent_error", "system", {"error": str(e)[:300]})
            await EVENT_BUS.close(self.run_id)

    async def _finish(self, profile_display: str, winner_offer: str | None, launch_url: str | None) -> None:
        duration_ms = int((time.time() - self._start_time) * 1000)
        summary = RunSummary(
            run_id=self.run_id,
            persona_display_name=profile_display,
            winner_offer_name=winner_offer,
            launch_url=launch_url,
            created_at=datetime.utcnow(),
            duration_ms=duration_ms,
        )
        await butterbase.save_run_summary(summary)
        await self._emit("run_complete", "system", {"run_id": self.run_id, "duration_ms": duration_ms,
                                                     "summary": summary.model_dump(mode="json")})
        await EVENT_BUS.close(self.run_id)
