import pytest

# We skip the entire module if Qiskit isn't installed
qiskit = pytest.importorskip("qiskit")

from qiskit import QuantumCircuit
from tuneq import optimize_circuit_for
from tuneq.exceptions import OptimizationError

def test_qiskit_optimize_simple_circuit():
    """Check if Qiskit's transpile is invoked successfully."""
    qc = QuantumCircuit(2)
    qc.h(0)
    qc.cx(0, 1)
    qc.measure_all()

    optimized = optimize_circuit_for(qc, optimization_level=1)
    # If everything works, we get a transpiled circuit back
    assert hasattr(optimized, "data"), "Optimized object should be a Qiskit QuantumCircuit"
    assert len(optimized.data) <= len(qc.data), "Optimization should not increase circuit size"

def test_qiskit_optimize_invalid_object():
    """Ensure we raise no exception if the object isn't a Qiskit circuit."""
    dummy_object = "NotAQiskitCircuit"
    optimized = optimize_circuit_for(dummy_object)
    assert optimized == dummy_object, "Should return the original object unchanged"

def test_qiskit_optimize_raises_error(monkeypatch):
    """Force an error inside Qiskit transpiler to see if we catch and raise OptimizationError."""
    from qiskit import QuantumCircuit

    def mock_transpile_fail(*args, **kwargs):
        raise ValueError("Mock transpile error")

    qc = QuantumCircuit(1)
    monkeypatch.setattr("qiskit.transpile", mock_transpile_fail)

    with pytest.raises(OptimizationError) as excinfo:
        optimize_circuit_for(qc)
    assert "Mock transpile error" in str(excinfo.value)
