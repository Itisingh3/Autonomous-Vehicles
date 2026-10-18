import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "experiments"))

from reputation_model import Event, ReputationConfig, ReputationModel, Severity

def event(node, typ, sev, round_no=1):
    return Event(node, typ, sev, float(round_no), "hash", round_no)

def test_recent_and_long_term_decay_differ():
    m = ReputationModel(["a"], ReputationConfig())
    m.record_round({"a": 1}, [])
    assert m.nodes["a"].recent < m.nodes["a"].long_term

def test_low_fault_forgiveness():
    cfg = ReputationConfig(rho=.5)
    m = ReputationModel(["a"], cfg)
    m.record_round({"a": 1}, [event("a", "delayed_valid", Severity.LOW)])
    assert m.nodes["a"].recent > 80

def test_critical_penalty_has_no_forgiveness():
    m = ReputationModel(["a"])
    m.record_round({"a": 1}, [event("a", "invalid_signature", Severity.CRITICAL)])
    assert m.nodes["a"].recent < 90

def test_window_expires_events():
    m = ReputationModel(["a"], ReputationConfig(window=2))
    for i in range(3): m.record_round({"a": 1}, [event("a", "conflicting_prepare", Severity.HIGH, i)])
    assert len(m.nodes["a"].events) == 2

def test_eligibility_preserves_pbft_minimum():
    m = ReputationModel([str(i) for i in range(13)], ReputationConfig(f=4))
    assert len(m.eligible()) >= 13

def test_revocation_requires_confirmation_unless_critical():
    m = ReputationModel(["a"], ReputationConfig(f=1))
    assert not m.confirm_revocation("a", 1)
    m.nodes["a"].recent = 0
    assert m.confirm_revocation("a", 3)

def test_critical_attack_cannot_recover():
    m = ReputationModel(["a"])
    assert m.confirm_revocation("a", 1, critical=True)
    m.record_round({"a": 1}, [])
    assert m.nodes["a"].role == "revoked"
