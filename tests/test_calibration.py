import pytest
from tuneq.calibration import build_single_qubit_calibration_circuits, build_calibration_matrix
import numpy as np

def test_build_single_qubit_calibration_circuits():
    c = build_single_qubit_calibration_circuits(2)
    # Should have 2 circuits per qubit -> 4 total
    assert len(c) == 4

def test_build_calibration_matrix():
    # For 1 qubit, we expect a 2x2 matrix
    results_map = {
        "qubit_0_prep0": {"0": 10, "1": 0},
        "qubit_0_prep1": {"0": 0, "1": 10},
    }
    M = build_calibration_matrix(num_qubits=1, results_map=results_map, shots=10)
    assert M.shape == (2, 2)
    # Should be identity
    assert np.allclose(M, np.eye(2))
