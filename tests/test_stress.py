# tests/test_stress.py

import pytest
from tuneq import mitigate_measurement_errors
from tuneq.circuit_spec import GenericCircuit

def bulk_runner(circuits, shots=2000, **kwargs):
    """
    A runner that simulates running many circuits with a fairly large shot count
    for 3 qubits. We'll do something trivial: 
    half the outcomes are '000', half are '111'.
    """
    results = []
    for c in circuits:
        results.append({"000": shots // 2, "111": shots // 2})
    return results

def test_mini_stress_calibration():
    """
    Runs calibration for 3 qubits (which yields 6 calibration circuits),
    plus executes 10 main circuits afterwards, each with 2000 shots.
    """
    with mitigate_measurement_errors(
        num_qubits=3,
        run_circuits=bulk_runner,
        shots=2000
    ) as mitigator:
        # We'll create 10 "main circuits"
        main_circuits = []
        for i in range(10):
            c = GenericCircuit(num_qubits=3)
            c.add_gate("X", [0])  # trivial gate
            main_circuits.append(c)

        results = []
        for mc in main_circuits:
            corrected = mitigator.run(mc)
            results.append(corrected)

    # Basic check: we got 10 results
    assert len(results) == 10
    for r in results:
        total_shots = sum(r.values())
        assert total_shots == 2000, "Total shots must remain consistent."
