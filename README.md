# TuneQ

A production-ready library for **measurement-error mitigation** and **circuit optimization** in NISQ computing.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![Contributions Welcome](https://img.shields.io/badge/Contributions-Welcome-brightgreen.svg)](#contributing)

---

## Table of Contents

1. [Overview](#overview)  
2. [Key Features](#key-features)  
3. [Installation](#installation)  
   - [Using Poetry](#using-poetry)  
   - [Using Requirements Files (pip)](#using-requirements-files-pip)  
4. [Usage](#usage)  
   - [Measurement-Error Mitigation](#measurement-error-mitigation)  
   - [Circuit Optimization](#circuit-optimization)  
   - [Example: Qiskit Integration](#example-qiskit-integration)  
   - [Example: Cirq Integration](#example-cirq-integration)  
5. [Contributing](#contributing)  
6. [License](#license)  

---

## Overview

**TuneQ** is designed to simplify two core tasks in NISQ (Noisy Intermediate-Scale Quantum) computing:

1. **Measurement-Error Mitigation**: Build calibration circuits, invert the resulting calibration matrices, and automatically correct readout errors in multi-qubit systems.
2. **Lightweight Circuit Optimization**: Detect whether you’re using **Qiskit** or **Cirq** and invoke the corresponding transpiler or optimizer with minimal fuss.

TuneQ helps researchers, developers, and quantum enthusiasts spend more time **focusing on their algorithms** and less time writing boilerplate code for calibration, error mitigation, or circuit optimization.

---

## Key Features

- **Single- or Multi-Qubit Readout Calibration**:
  - Tensor-product approach for multi-qubit calibration.
  - Automatically builds and runs calibration circuits, then creates an error-mitigation matrix.
  - Applies matrix inversion to **correct** measurement results.

- **One-Line Circuit Optimization**:
  - **Auto-detects** whether you’re using Qiskit or Cirq.
  - Leverages native transpile/optimization passes from each framework.
  - Bypasses complex pass-manager setups in Qiskit or advanced transformations in Cirq.

- **Flexible & Framework-Agnostic**:
  - No forced login to specific quantum cloud providers.
  - Users provide their own function to run circuits on any backend (real device or simulator).

- **Error Handling & Diagnostics**:
  - Custom exceptions (`CalibrationError`, `OptimizationError`) provide clear feedback.
  - Handles ill-conditioned calibration matrices gracefully.

---

## Installation

TuneQ supports **Python 3.10+**. You can install via **Poetry** or generate a `requirements.txt` for pip.

### Using Poetry

1. **Clone** the repo:

   ```bash
   git clone https://github.com/<your-username>/tuneq.git
   cd tuneq
   ````
2. **Install** with poetry:
    

    ```bash
    poetry install
    ````
    By default, TuneQ installs only the core dependencies (e.g numpy). To enable Qiskit or Cirq integrations:

   ```bash
   poetry install --extras "qiskit"
   poetry install --extras "cirq"
   ````

3. **Run Tests**
    ```bash
    poetry run pytest
    ````

## Usage

### Measurement-Error Mitigation

```python
from tuneq import mitigate_measurement_errors

with mitigate_measurement_errors(
    num_qubits=2,
    run_circuits=my_runner_function,
    shots=1024
) as mitigator:
    corrected_counts = mitigator.run(my_main_circuit)
````

### Circuit Optimization

```python
from tuneq import optimize_circuit_for

optimized_circuit = optimize_circuit_for(my_circuit, optimization_level=2)
```

### Qiskit Example

```python
from qiskit import QuantumCircuit, Aer, transpile
from tuneq import mitigate_measurement_errors, optimize_circuit_for

qc = QuantumCircuit(2)
qc.h(0)
qc.cx(0, 1)
qc.measure_all()

def qiskit_runner(circuits, shots=1024):
    simulator = Aer.get_backend('qasm_simulator')
    return [simulator.run(transpile(c, simulator), shots=shots).result().get_counts() for c in circuits]

with mitigate_measurement_errors(num_qubits=2, run_circuits=qiskit_runner, shots=1024) as mitigator:
    corrected_counts = mitigator.run(qc)

optimized_qc = optimize_circuit_for(qc, optimization_level=3)

````

## Contributing

We welcome contributions! Feel free to:

- Open an issue to report bugs or suggest features.
- Submit a pull request for fixes or new features.
- Join discussions to collaborate on improvements.

---

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

