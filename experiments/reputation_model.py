"""Explainable sliding-window reputation model; deliberately contains no ML."""
from __future__ import annotations
from dataclasses import dataclass, field
from collections import deque
from enum import IntEnum
from typing import Iterable

class Severity(IntEnum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4

PENALTIES = {Severity.LOW: 1.0, Severity.MEDIUM: 2.0, Severity.HIGH: 5.0, Severity.CRITICAL: 15.0}
OMEGA = {Severity.LOW: .2, Severity.MEDIUM: .5, Severity.HIGH: 1.0, Severity.CRITICAL: 2.0}
NO_FORGIVENESS = {"invalid_signature", "sybil", "false_position", "collusion", "conflicting_prepare", "conflicting_commit"}

@dataclass(frozen=True)
class ReputationConfig:
    alpha: float = 1.0; beta_high: float = 5.0; gamma: float = 2.0
    lambda_recent: float = .10; lambda_long: float = .01; window: int = 20
    rho: float = .5; theta1: float = 1.0; theta2: float = 2.0; theta3: float = 4.0
    reassignment_window: int = 20; f: int = 4; epsilon: float = .05
    beta_low: float = 1.0; beta_medium: float = 2.0; beta_critical: float = 15.0; beta_collusion: float = 20.0
    @property
    def penalties(self):
        return {Severity.LOW:self.beta_low, Severity.MEDIUM:self.beta_medium, Severity.HIGH:self.beta_high, Severity.CRITICAL:self.beta_critical}

@dataclass(frozen=True)
class Event:
    node_id: str; event_type: str; severity: Severity; timestamp: float; evidence_hash: str; round_no: int

@dataclass
class NodeState:
    node_id: str; recent: float = 100.0; long_term: float = 100.0
    events: deque[Event] = field(default_factory=deque); role: str = "trusted"; revoked: bool = False

class ReputationModel:
    def __init__(self, node_ids: Iterable[str], config: ReputationConfig = ReputationConfig()):
        self.config = config; self.nodes = {str(n): NodeState(str(n)) for n in node_ids}; self.round = 0

    def _accuracy(self, state: NodeState) -> float:
        evaluated = len(state.events)
        return sum(e.event_type == "valid_contribution" for e in state.events) / evaluated if evaluated else 0.0

    def _penalty(self, event: Event, state: NodeState) -> float:
        base = self.config.penalties[event.severity]
        if event.event_type == "collusion": base = self.config.beta_collusion
        if event.severity <= Severity.MEDIUM and event.event_type not in NO_FORGIVENESS:
            base *= (1.0 - self.config.rho * self._accuracy(state))
        return base

    def record_round(self, contributions: dict[str, int], events: Iterable[Event], timestamp: float | None = None):
        self.round += 1; by_node = {n: list(contributions.get(n, 0) and [] or []) for n in self.nodes}
        for event in events: by_node.setdefault(event.node_id, []).append(event)
        for node_id, state in self.nodes.items():
            ev = by_node.get(node_id, []); valid = int(contributions.get(node_id, 0)); delta = self.config.alpha * valid
            for event in ev: delta -= self._penalty(event, state)
            state.events.extend(ev)
            while len(state.events) > self.config.window: state.events.popleft()
            state.recent = max(0.0, min(100.0, (1-self.config.lambda_recent)*state.recent + delta))
            state.long_term = max(0.0, min(100.0, (1-self.config.lambda_long)*state.long_term + delta))
        self.update_roles()

    def maliciousness(self, node_id: str) -> float:
        return sum(OMEGA[e.severity] for e in self.nodes[node_id].events)

    def update_roles(self):
        vals = [n.recent for n in self.nodes.values() if not n.revoked]
        if not vals: return
        mu = sum(vals)/len(vals); sigma = (sum((x-mu)**2 for x in vals)/len(vals))**.5
        for state in self.nodes.values():
            if state.revoked: state.role = "revoked"; continue
            score = self.maliciousness(state.node_id)
            if score >= self.config.theta3: state.role = "quarantined"
            elif score >= self.config.theta2: state.role = "quarantined"
            elif score >= self.config.theta1: state.role = "suspicious"
            elif state.recent < mu-sigma: state.role = "candidate"
            else: state.role = "trusted"

    def eligible(self) -> list[str]:
        vals = [n.recent for n in self.nodes.values() if not n.revoked and n.role != "quarantined"]
        if not vals: return []
        mu = sum(vals)/len(vals); sigma = (sum((x-mu)**2 for x in vals)/len(vals))**.5; high = mu+sigma
        eligible = [n.node_id for n in self.nodes.values() if not n.revoked and n.role != "quarantined" and n.recent >= high]
        minimum = 3*self.config.f + 1
        if len(eligible) < minimum:
            eligible = sorted((n.node_id for n in self.nodes.values() if not n.revoked and n.role != "quarantined"), key=lambda x:self.nodes[x].recent, reverse=True)[:minimum]
        return eligible

    def confirm_revocation(self, node_id: str, confirmations: int, critical: bool = False) -> bool:
        state = self.nodes[node_id]
        if critical or (state.recent <= 0 and confirmations >= 2*self.config.f+1):
            state.revoked = True; state.role = "revoked"; return True
        return False

    def trajectory(self, node_id: str):
        return self.nodes[node_id].recent, self.nodes[node_id].long_term, self.nodes[node_id].role
