"""Utility functions for tests."""

import json
from typing import List, Dict


def load_test_data(filepath: str) -> List[Dict]:
    """Load JSON test data from file."""
    with open(filepath, 'r') as f:
        return json.load(f)


def assert_almost_equal(a, b, epsilon=1e-6):
    """Test helper."""
    assert abs(a - b) < epsilon, f"{a} != {b}"