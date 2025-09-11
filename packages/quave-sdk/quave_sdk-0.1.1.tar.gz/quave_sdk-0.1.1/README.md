# Quave SDK

`quave-sdk` provides a Python interface to Quave's platform for executing 
quantum circuits, and retrieving results in hybrid quantum-classical workflows. 

## Installation

```bash
# For users
pip install quave-sdk

# For developers
pip install -e .
```

## Usage

```python
from qiskit import QuantumCircuit
from quave_sdk.quave import Quave

# --- 1. Authentication ---

# initialize a quave object using environment variable authentication
import os
email = os.getenv("EMAIL")
password = os.getenv("PASSWORD")
quave = Quave(email, password)

# or using command line inputs
quave = Quave()


# --- 2. View Backends ---

# see all available backends
backends = quave.list_backends()

# or for a specific QPU provider
backends = quave.list_backends("ibm")

# retrieve statistics for a specific backend
backend_stats = quave.get_backend_stats(backend_name="ibm_brisbane", provider="ibm")


# --- 3. Simple Execution (No Parameters) ---

# build a simple circuit
qc = QuantumCircuit(1)
qc.h(0)
qc.t(0)
qc.measure_all()

# execute the circuit
job = quave.execute(circuit=qc, shots=10, backend="simulate")

# check the status and retrieve counts
status = job.get_status()
if status == "COMPLETED":
    execution = job.get_executions()[0]
    counts = execution.get_counts()

# or wait for the job to be complete
asyncio.run(job.await_completion())
execution = job.get_executions()[0]
counts = execution.get_counts()

# --- 4. Batch Execution (Parameterized Circuit) ---

# define a simple parameterized circuit
theta = Parameter("θ")
qc = QuantumCircuit(1, 1)
qc.rx(theta, 0)
qc.measure(0, 0)

# define parameter values
params = [{"θ": x} for x in range(0, 90, 10)]

# execute the job and await completion
job = quave.execute(circuit=qc, parameters=params, shots=10, backend="simulate")
asyncio.run(job.await_completion())

# retrieve counts for each execution
executions = job.get_executions()
for x in executions:
    print(f"Counts for parameters {x.parameters}: {x.get_counts()}")


# --- 5. Iterative Execution ---

# define a function to generate new parameters from result counts
from math import pi

def update_parameters(counts):
    if counts.get("0", 0) > 0:
        return {"θ": pi}
    else:
        return {"θ": 0}

# execute the iterative workload
job = asyncio.run(quave.iterative_execute(
    circuit=qc, 
    parameter_update_fn=update_parameters, 
    initial_parameters={"θ": 0}, 
    num_iterations=3, 
    shots=10, 
    backend="simulate"
))

# retrieve the counts for each iteration
executions = job.get_executions()
for x in executions:
    print(f"Counts for parameters {x.parameters}: {x.get_counts()}")

```

