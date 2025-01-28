"""
Implements a one-liner (context manager) for building calibration circuits, running them,
building the calibration matrix, and then applying it to user circuits.

The user must provide:
  1) num_qubits
  2) run_circuits(...) -> a function that can take a list of GenericCircuit (or user circuits)
     and return the measurement results as a dict of {bitstring: count} or list of such dicts
  3) Shots, etc.
"""

import contextlib
import numpy as np
from typing import Any, Callable, Dict, List, Union
from .calibration import build_single_qubit_calibration_circuits, build_calibration_matrix
from .circuit_spec import GenericCircuit
from .exceptions import CalibrationError
import copy


def apply_mitigation(raw_counts: Dict[str, int], mitigation_matrix: np.ndarray) -> Dict[str, int]:
    """
    Apply the inverse of the mitigation_matrix to the raw probability distribution
    and return corrected counts. The matrix is dimension 2^N x 2^N.

    raw_counts: {bitstring: count}
    We:
     1) Convert to a probability vector of length 2^N (assuming bitstring indexing).
     2) Multiply by M^{-1}.
     3) Clip negative probabilities to 0, renormalize.
     4) Convert back to integer counts (approx).
    """

    all_bitstrings = list(raw_counts.keys())
    total_shots = sum(raw_counts.values())
    if total_shots == 0:
        return raw_counts  # can't do anything

    # Convert to probability vector in ascending bitstring order or some canonical order
    # We'll define that the 0-based index = integer value of bitstring reversed for N qubits
    # for convenience. E.g. for 2 qubits:
    # bitstring '00' -> index 0
    # bitstring '01' -> index 1
    # bitstring '10' -> index 2
    # bitstring '11' -> index 3
    # In general: int(bitstring[::-1], 2)
    # We'll fill in probabilities for any missing bitstrings as 0.
    num_qubits = len(all_bitstrings[0]) if all_bitstrings else 0
    vector_size = 2 ** num_qubits
    prob_vector = np.zeros(vector_size, dtype=float)

    for bs, cnt in raw_counts.items():
        idx = int(bs[::-1], 2)
        prob_vector[idx] = cnt / total_shots

    # Invert the matrix to get M^-1
    try:
        minv = np.linalg.inv(mitigation_matrix)
    except np.linalg.LinAlgError:
        # If the matrix is singular or ill-conditioned, can't invert
        return raw_counts

    corrected_probs = minv @ prob_vector

    # clip negative probabilities and re-normalize
    corrected_probs = np.clip(corrected_probs, 0, None)
    norm = np.sum(corrected_probs)
    if norm > 0:
        corrected_probs /= norm

    # convert back to counts
    corrected_counts = {}
    for i in range(vector_size):
        bitstr = format(i, f'0{num_qubits}b')[::-1]
        corrected_counts[bitstr] = int(round(corrected_probs[i] * total_shots))

    return corrected_counts


@contextlib.contextmanager
def mitigate_measurement_errors(
    num_qubits: int,
    run_circuits: Callable,
    shots: int = 1024,
    **kwargs
):
    """
    A context manager that:
     1. Builds single-qubit calibration circuits
     2. Calls `run_circuits(calib_circuits)` to get their measurement results
     3. Builds the big calibration matrix
     4. Yields a 'mitigator' object that can .run(your_circuit) -> returns corrected counts.

    The user must supply:
      - num_qubits
      - run_circuits: a function that takes a list of GenericCircuit (or any circuit format) and
        returns a list/dict of measurement outcomes in the form {bitstring: count}.

    Usage:
    ```python
    with mitigate_measurement_errors(num_qubits=2, run_circuits=my_runner) as mitigator:
        corrected_counts = mitigator.run(my_main_circuit)
    ```
    """

    # 1. Build calibration circuits
    calibration_specs = build_single_qubit_calibration_circuits(num_qubits)
    # calibration_specs is a list of (GenericCircuit, label)

    # 2. Run them
    circuits_only = [spec[0] for spec in calibration_specs]
    labels_only = [spec[1] for spec in calibration_specs]

    raw_results_list = run_circuits(circuits_only, shots=shots, **kwargs)
    # Expecting raw_results_list to be a list of dicts with the same length as circuits_only
    # Each dict = {bitstring: count}

    if not isinstance(raw_results_list, list):
        raise CalibrationError("run_circuits must return a list of result dicts for calibration circuits.")

    if len(raw_results_list) != len(circuits_only):
        raise CalibrationError("Number of returned results does not match number of calibration circuits.")

    # 3. Build results_map for each label
    results_map = {}
    for label, result in zip(labels_only, raw_results_list):
        results_map[label] = result

    # 4. Build calibration matrix
    calibration_matrix = build_calibration_matrix(num_qubits, results_map, shots)

    class Mitigator:
        def run(self, circuit: Any, raw_counts: Dict[str, int] = None, **run_kwargs) -> Dict[str, int]:
            """
            Execute `circuit` via `run_circuits` if raw_counts is None,
            then apply measurement-error mitigation.
            
            If the user already has raw_counts from somewhere else, they can pass it.
            """
            if raw_counts is None:
                # We'll run the circuit ourselves
                circuit_list = [circuit]
                circuit_results = run_circuits(circuit_list, shots=shots, **run_kwargs)
                raw_counts = circuit_results[0]

            # Apply readout mitigation
            corrected = apply_mitigation(raw_counts, calibration_matrix)
            return corrected

    try:
        yield Mitigator()
    finally:
        pass
