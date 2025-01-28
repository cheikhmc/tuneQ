"""
A function that detects the type of circuit (Qiskit, Cirq, PyQuil) and applies an
appropriate optimization or transpilation routine. If detection fails or isn't supported,
we do a simple pass-through.
"""

from typing import Any
from .detection import is_qiskit_installed, is_cirq_installed
from .exceptions import OptimizationError

def optimize_circuit_for(circuit: Any, optimization_level: int = 3) -> Any:
    """
    Attempt to optimize the given circuit. We'll:
     1. Detect if it's a Qiskit, Cirq, or PyQuil circuit
     2. Call the relevant transpiler/optimizer if installed
     3. Otherwise, return circuit unchanged

    Args:
        circuit: Qiskit QuantumCircuit, Cirq Circuit, PyQuil Program, or unknown
        optimization_level: For Qiskit, this is an integer 0-3 controlling how aggressive.

    Returns:
        An optimized version of the circuit (or the same object if no optimization possible).
    """
    # Detect Qiskit
    if is_qiskit_installed():
        try:
            from qiskit import QuantumCircuit, transpile
            if isinstance(circuit, QuantumCircuit):
                return transpile(circuit, optimization_level=optimization_level)
        except Exception as ex:
            raise OptimizationError(f"Qiskit optimization failed: {ex}")

    # Detect Cirq
    if is_cirq_installed():
        try:
            import cirq
            if isinstance(circuit, cirq.Circuit):
                # Example: use built-in optimizers
                # We apply a chain of standard cirq optimizations:
                optimized = cirq.Circuit(circuit)  # make a copy
                transforms = [
                    cirq.MergeSingleQubitGates(),
                    cirq.DropEmptyMoments(),
                    cirq.EjectPhasedPaulis(),
                    cirq.SynchronizeTerminalMeasurements(),
                ]
                for transform in transforms:
                    optimized = transform(optimized)
                return optimized
        except Exception as ex:
            raise OptimizationError(f"Cirq optimization failed: {ex}")

    return circuit
