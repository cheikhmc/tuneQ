"""
Build single-qubit calibration circuits for each qubit, then combine the results
to form a multi-qubit calibration matrix via tensor products.

We provide a standard approach:
    - For each qubit i:
        1) Prepare |0>, measure
        2) Prepare |1>, measure
    - Convert those results into a 2x2 matrix for that qubit:
        M_i = [[P(meas=0|prep=0), P(meas=1|prep=0)],
               [P(meas=0|prep=1), P(meas=1|prep=1)]]
    - For multiple qubits, the final matrix is the tensor product of each M_i.
"""

import numpy as np
from typing import List, Callable, Dict
from .circuit_spec import GenericCircuit
from .exceptions import CalibrationError

def build_single_qubit_calibration_circuits(num_qubits: int):
    """
    For each qubit i, we build two circuits:
        - Prep qubit i in |0>, measure
        - Prep qubit i in |1>, measure
      The other qubits remain in |0>.

    Returns a list of (circuit, label) so we can track which is which.
    """
    all_calibration_circuits = []

    for qubit in range(num_qubits):
        # 1) Prep |0> on qubit
        c0 = GenericCircuit(num_qubits=num_qubits)
        # no explicit gate needed for |0>, but let's measure all to be consistent
        c0.measure_all()
        label0 = f"qubit_{qubit}_prep0"

        # 2) Prep |1> on qubit
        c1 = GenericCircuit(num_qubits=num_qubits)
        c1.add_gate("X", [qubit])  # flip from |0> to |1>
        c1.measure_all()
        label1 = f"qubit_{qubit}_prep1"

        all_calibration_circuits.append((c0, label0))
        all_calibration_circuits.append((c1, label1))

    return all_calibration_circuits

def build_calibration_matrix(num_qubits: int, results_map: Dict[str, Dict[str, int]], shots: int) -> np.ndarray:
    """
    Using the results of the calibration circuits, build a single-qubit 2x2 matrix for each qubit,
    then take the tensor product of all qubits' matrices to get a final 2^(num_qubits) x 2^(num_qubits) matrix.

    results_map is a dictionary like:
        {
          'qubit_0_prep0': {'0...': count, '1...': count, ...},
          'qubit_0_prep1': {...},
          'qubit_1_prep0': {...},
          ...
        }

    We'll assume only relevant bits for each qubit's measurement matter. 
    This is still an approximation because it ignores correlated errors.
    """
    if shots <= 0:
        raise CalibrationError("Invalid number of shots for calibration.")

    # We'll store a list of 2x2 matrices for each qubit
    qubit_matrices = []
    for qubit in range(num_qubits):
        label0 = f"qubit_{qubit}_prep0"
        label1 = f"qubit_{qubit}_prep1"
        if label0 not in results_map or label1 not in results_map:
            raise CalibrationError(f"Missing calibration data for qubit {qubit}.")

        # Single qubit results for prep0
        counts_prep0 = results_map[label0]  # {bitstring: count}
        # Single qubit results for prep1
        counts_prep1 = results_map[label1]

        # Probability that we measure qubit 'qubit' as 0 or 1
        # We'll extract that qubit's bit from the bitstring (assuming little-endian or big-endian?).
        # Let's assume the qubit index is from right to left for simplicity.
        # If user’s measurement ordering is different, they'd adapt. 
        p_meas0_given_prep0 = 0
        p_meas1_given_prep0 = 0
        total0 = sum(counts_prep0.values())

        for bitstring, cnt in counts_prep0.items():
            # if the qubit-th bit from the right is '0', then we measured 0
            if bitstring[::-1][qubit] == '0':
                p_meas0_given_prep0 += cnt
            else:
                p_meas1_given_prep0 += cnt

        # Similarly for prep1
        p_meas0_given_prep1 = 0
        p_meas1_given_prep1 = 0
        total1 = sum(counts_prep1.values())

        for bitstring, cnt in counts_prep1.items():
            if bitstring[::-1][qubit] == '0':
                p_meas0_given_prep1 += cnt
            else:
                p_meas1_given_prep1 += cnt

        # Convert to probabilities
        if total0 == 0 or total1 == 0:
            raise CalibrationError(f"No counts found for qubit {qubit} prep states. Shots might be zero?")

        p_meas0_given_prep0 /= total0
        p_meas1_given_prep0 /= total0
        p_meas0_given_prep1 /= total1
        p_meas1_given_prep1 /= total1

        # Single-qubit 2x2 matrix
        # Row = prepared state, col = measured state
        # M_i = [[P(0|0), P(1|0)],
        #        [P(0|1), P(1|1)]]
        M_i = np.array([
            [p_meas0_given_prep0, p_meas1_given_prep0],
            [p_meas0_given_prep1, p_meas1_given_prep1]
        ])
        qubit_matrices.append(M_i)

    # Combine them with a tensor product
    final_matrix = np.array([[1.0]])
    for M_i in qubit_matrices:
        final_matrix = np.kron(final_matrix, M_i)

    return final_matrix
