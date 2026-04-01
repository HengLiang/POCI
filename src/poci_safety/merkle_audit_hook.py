"""
Merkle tree audit hook for zero‑trust integration.
"""

from typing import Dict, List, Tuple
import hashlib


class MerkleAuditHook:
    def __init__(self, batch_threshold: float = 0.4):
        self.batch_threshold = batch_threshold
        self.leaf_db = {}

    def validate_leaf(self, leaf: Dict) -> Tuple[bool, str]:
        """Re‑implement validation for audit trail."""
        if leaf.get("origin_type") == "AI_GENERATED":
            return False, "direct_ai_generation"
        for pid in leaf.get("parent_leaf_ids", []):
            parent = self.leaf_db.get(pid)
            if parent and parent.get("origin_type") == "AI_GENERATED":
                return False, f"ai_ancestor_detected: {pid}"
        if not leaf.get("zk_proof_valid", True):
            return False, "invalid_zk_proof"
        return True, "ACCEPT"

    def audit_batch(self, leaves: List[Dict]) -> Dict:
        """Audit a batch and produce report."""
        ai_assisted = 0
        total = len(leaves)
        for leaf in leaves:
            if leaf.get("origin_type") == "AI_ASSISTED":
                ai_assisted += 1
        ratio = ai_assisted / total if total else 0.0
        alert = ratio > self.batch_threshold
        return {
            "ai_assisted_ratio": ratio,
            "alert_triggered": alert,
            "alert_type": "BATCH_RATIO_EXCEEDED" if alert else None,
        }

    def record_leaf(self, leaf: Dict):
        """Store leaf for future ancestor checks."""
        leaf_id = leaf.get("leaf_id")
        if leaf_id:
            self.leaf_db[leaf_id] = leaf