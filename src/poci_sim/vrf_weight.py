"""
VRF-based committee selection with logarithmic weight function.
"""

import math
import hashlib
import struct
from typing import List, Dict, Optional

DEFAULT_PARAMS = {
    "w_base": 1.0,
    "r_half": 20,
    "w_cap": 3.0,
    "penalty_threshold": 5
}

class InsufficientCandidatesError(Exception):
    pass

def vrf_weight(reputation_score: int, params: Optional[Dict] = None) -> float:
    """
    VRF weight function with logarithmic saturation and soft penalty.
    """
    if params is None:
        params = DEFAULT_PARAMS
    r = reputation_score
    if r < 0:
        return 0.0

    w_base = params["w_base"]
    r_half = params["r_half"]
    w_cap = params["w_cap"]
    penalty_threshold = params["penalty_threshold"]

    # Core logarithmic saturation
    raw = w_base * (1.0 + math.log(1.0 + r / r_half))
    weight = min(raw, w_cap)

    # Soft penalty for low reputation
    if r < penalty_threshold:
        weight *= r / penalty_threshold

    return weight

def sample_committee(candidates: List[Dict],
                     vrf_seed: bytes,
                     committee_size: int = 21,
                     params: Optional[Dict] = None) -> List[str]:
    """
    Weighted sampling without replacement using Efraimidis-Spirakis algorithm.
    candidates: list of dicts with keys "node_id", "reputation", "stake"
    Returns list of selected node_ids.
    """
    if params is None:
        params = DEFAULT_PARAMS

    # Filter eligible nodes (stake >= 1000, reputation >=0)
    eligible = [c for c in candidates if c.get("stake", 0) >= 1000 and c.get("reputation", 0) >= 0]
    if len(eligible) < committee_size:
        raise InsufficientCandidatesError(f"Need {committee_size}, got {len(eligible)}")

    # Compute weight for each eligible node
    weights = [vrf_weight(c["reputation"], params) for c in eligible]
    # Generate random priority scores based on VRF seed and node_id
    def priority(node, weight):
        # Combine seed and node_id to produce deterministic random
        h = hashlib.sha256(vrf_seed + node["node_id"].encode()).digest()
        u = struct.unpack(">Q", h[:8])[0] / (2**64)  # uniform [0,1)
        # Exponential priority: -log(u) / weight
        return -math.log(u + 1e-15) / weight

    scored = sorted(eligible, key=lambda n: priority(n, vrf_weight(n["reputation"], params)))
    selected = [n["node_id"] for n in scored[:committee_size]]
    return selected