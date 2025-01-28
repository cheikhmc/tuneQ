import pytest
from tuneq.optimizer import optimize_circuit_for

def test_optimize_fallback():
    # If it's not a recognized circuit, we get the same object back
    dummy = "not_a_real_circuit"
    result = optimize_circuit_for(dummy)
    assert result == dummy
