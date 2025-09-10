# Quantum Scoring SDK v0.3.0

Quantum-native framework with IBM Quantum hardware support.

## Installation

### Basic (with simulator)
pip install quantum-scoring-sdk

### With IBM Quantum support
pip install quantum-scoring-sdk[ibm]

## Features
- Built-in quantum simulator
- IBM Quantum hardware support
- F1=0.774 demonstrated on real hardware
- No PhD required

## Usage

### Simulator (default)
from quantum_sdk import Optimizer
opt = Optimizer()
score = opt.evaluate(data, config)

### IBM Quantum Hardware
from quantum_sdk import Optimizer
opt = Optimizer()
opt.configure_ibm(token='YOUR_IBM_TOKEN', backend='ibm_brisbane')
score = opt.evaluate(data, config, backend='ibm_brisbane')

## License
Proprietary. Contact jaimeajl@hotmail.com
