"""
Full integration tests for POCI simulation toolkit.
"""

import pytest
from src.poci_sim import (
    CXLLatencySimulator,
    DASSScheduler,
    ThermalCalculator,
    MerkleSimulator,
    vrf_weight,
    sample_committee,
    CommitteeAMTC,
    ZeroTrustChannel,
    ZKProofInterface
)


def test_cxl_latency():
    sim = CXLLatencySimulator()
    metrics = sim.compute_latency(arrival_rate=3e6)  # 3 million packets/sec
    assert metrics["P99_9_ns"] <= sim.redline_ns
    assert metrics["rho"] < 0.85


def test_dass_scheduler():
    scheduler = DASSScheduler()
    res = scheduler.schedule_step(total_work=1e12, current_temp_A=70, current_temp_B=65)
    assert 0 <= res["S_A"] <= 1
    assert 0 <= res["S_B"] <= 1
    assert res["total_latency"] > 0


def test_thermal_calculator():
    calc = ThermalCalculator()
    res = calc.evaluate(dummy_packet_rate=10)
    assert res["Tj_celsius"] <= 85
    assert res["thermal_safety_margin"] >= 0


def test_merkle_simulator():
    sim = MerkleSimulator()
    leaf = {
        "origin_type": "HUMAN_ORIGINAL",
        "parent_leaf_ids": [],
        "zk_proof_valid": True
    }
    accept, reason = sim.validate_leaf(leaf)
    assert accept
    assert reason == "ACCEPT"

    batch = [leaf] * 10
    batch[5]["origin_type"] = "AI_ASSISTED"
    result = sim.batch_validate(batch)
    assert result["ai_assisted_ratio"] == 0.5
    assert result["batch_alert_triggered"]  # >40%


def test_vrf_weight():
    w = vrf_weight(10)
    assert 1.5 < w < 2.5
    w0 = vrf_weight(0)
    assert w0 == 0.0
    w_high = vrf_weight(1000)
    assert w_high <= 3.0


def test_committee_sampling():
    candidates = [
        {"node_id": "A", "reputation": 100, "stake": 2000},
        {"node_id": "B", "reputation": 20, "stake": 1500},
        {"node_id": "C", "reputation": 5, "stake": 1000},
        {"node_id": "D", "reputation": 0, "stake": 500},
        {"node_id": "E", "reputation": 50, "stake": 3000},
    ] * 10
    seed = b"test_seed_123"
    selected = sample_committee(candidates, seed, committee_size=21)
    assert len(selected) == 21
    # Zero reputation node (D) may be excluded by stake<1000 filter
    assert "D" not in selected


def test_amtc():
    real_packets = [
        {"size": 105, "iat": 0, "direction": "up", "phase": "vote"},
        {"size": 936, "iat": 200, "direction": "down", "phase": "aggregate"},
    ]
    amtc = CommitteeAMTC()
    morphed, metrics = amtc.morph_committee_flow(real_packets)
    assert metrics["aggregate_identifiable"] is True
    assert metrics["dummy_packet_count"] > 0


def test_zero_trust():
    zt = ZeroTrustChannel()
    cert = zt.derive_cert(b"fake_pubkey")
    assert cert["node_id"] == hashlib.sha256(b"fake_pubkey").hexdigest()
    packet = {"is_dummy": True, "hmac_valid": True}
    audit = zt.audit_sidecar(packet)
    assert audit["status"] == "PASS"


def test_zk_proof():
    params = {
        "features": {
            "lexical_entropy": {"weight": 0.25, "decision_boundary": 4.35},
            "ngram_repetition_density": {"weight": 0.10, "decision_boundary": 0.10},
            "natural_error_rate": {"weight": 0.10, "decision_boundary": 0.005},
            # ... other features would be present in real config
        }
    }
    # Minimal mock of other features (for testing)
    for feat in ["syntactic_depth_variance", "paragraph_length_cv", "punctuation_diversity_index"]:
        params["features"][feat] = {"weight": 0.15, "decision_boundary": 3.0}
    zk = ZKProofInterface(params)
    features = zk.extract_features("test text")
    result = zk.classify_authorship(features)
    assert "is_human" in result