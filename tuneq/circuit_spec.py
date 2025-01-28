"""
Defines how we represent calibration circuits in a generic manner. Researchers can
either convert these specs to Qiskit/Cirq/PyQuil circuits or implement direct runs.
"""

from dataclasses import dataclass
from typing import List

@dataclass
class GenericGate:
    name: str
    qubit_indices: List[int]

@dataclass
class GenericCircuit:
    num_qubits: int
    gates: List[GenericGate] = None
    measurement_qubits: List[int] = None

    def __post_init__(self):
        if self.gates is None:
            self.gates = []
        if self.measurement_qubits is None:
            self.measurement_qubits = list(range(self.num_qubits))

    def add_gate(self, gate_name: str, qubits: List[int]):
        self.gates.append(GenericGate(gate_name, qubits))

    def measure_all(self):
        self.measurement_qubits = list(range(self.num_qubits))
