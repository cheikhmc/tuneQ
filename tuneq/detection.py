"""
Attempt to detect which quantum frameworks (Qiskit, Cirq, PyQuil) are installed.
This helps us decide how to optimize circuits automatically.
"""

import importlib

def is_qiskit_installed() -> bool:
    return importlib.util.find_spec("qiskit") is not None

def is_cirq_installed() -> bool:
    return importlib.util.find_spec("cirq") is not None

