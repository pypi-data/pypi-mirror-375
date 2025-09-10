# quantum_sdk/core.py - Versión Quantum-Native con Simulador
import numpy as np
from sklearn.preprocessing import MinMaxScaler

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.providers.aer import AerSimulator
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

def normalize_data(data):
    """Normalize input data to [0,1] for quantum amplitude encoding."""
    normalized = {}
    for key, values in data.items():
        values = np.array(values).reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        normalized[key] = scaler.fit_transform(values).flatten().tolist()
    return normalized

def apply_non_linear(value, adjustments, lambdas):
    """Apply non-linear adjustments - core transformation."""
    adjusted = value
    for adj, lam in zip(adjustments, lambdas):
        adjusted += lam * adj
    return max(0.0, min(1.0, adjusted))

def build_quantum_circuit(values, weights, criticalities, penalty=0.0):
    """
    Build quantum circuit for hierarchical scoring.
    Maps normalized values to quantum amplitudes.
    """
    n = len(values)
    qc = QuantumCircuit(n + 1)  # n data qubits + 1 ancilla
    
    # Normalize weights considering criticalities
    wc = np.array(weights) * np.array(criticalities)
    norm = wc.sum()
    if norm == 0:
        norm = 1.0
    probs = wc / norm
    
    # Encode values as rotation angles
    for i in range(n):
        # Apply penalty to effective value
        effective_value = values[i] * (1.0 - penalty)
        # Convert to rotation angle weighted by importance
        angle = 2.0 * np.arcsin(np.sqrt(min(effective_value * probs[i], 1.0)))
        qc.ry(angle, i)
    
    # Weighted entanglement with ancilla
    ancilla = n
    for i in range(n):
        control_angle = np.pi * probs[i]
        qc.cry(control_angle, i, ancilla)
    
    # Add measurements
    qc.measure_all()
    
    return qc

def quantum_evaluate_block(values, weights, criticalities, penalty=0.0, 
                          lambdas=None, adjustments=None, shots=1024):
    """Evaluate single block using quantum circuit."""
    if not QUANTUM_AVAILABLE:
        raise ImportError("Qiskit not installed. Install with: pip install qiskit")
    
    # Apply non-linear adjustments if provided
    if lambdas and adjustments:
        values = [
            apply_non_linear(v, adjustments[i], lambdas)
            for i, v in enumerate(values)
        ]
    
    # Build and execute quantum circuit
    qc = build_quantum_circuit(values, weights, criticalities, penalty)
    
    # Use Aer simulator
    backend = AerSimulator()
    qc_transpiled = transpile(qc, backend)
    
    # Execute circuit
    job = backend.run(qc_transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Extract score from ancilla measurements
    ancilla_ones = 0
    total = 0
    n_qubits = len(values) + 1
    ancilla_pos = 0  # Ancilla is rightmost in bit string
    
    for bitstring, count in counts.items():
        if bitstring[ancilla_pos] == '1':
            ancilla_ones += count
        total += count
    
    # Score based on ancilla probability
    score = ancilla_ones / (total + 1e-12)
    
    # Apply entropy bonus for quantum advantage
    if len(counts) > 1:
        probs = np.array(list(counts.values())) / total
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = min(np.log2(2**n_qubits), np.log2(shots))
        entropy_factor = 1.0 + 0.1 * (entropy / (max_entropy + 1e-12))
        score = min(1.0, score * entropy_factor)
    
    return score

def hierarchical_quantum_score(blocks, global_penalty=0.0, shots=1024):
    """
    Hierarchical quantum scoring across multiple blocks.
    """
    sub_scores = []
    global_weights = []
    global_criticalities = []
    
    for block in blocks:
        score = quantum_evaluate_block(
            block['values'],
            block['weights'],
            block['criticalities'],
            penalty=block.get('penalty', 0.0),
            lambdas=block.get('lambdas', []),
            adjustments=block.get('adjustments', []),
            shots=shots
        )
        sub_scores.append(score)
        global_weights.append(block.get('global_weight', 1.0))
        global_criticalities.append(block.get('global_criticality', 1.0))
    
    # Aggregate sub-scores (could also be quantum but kept classical for speed)
    final_weighted = [s * w * c for s, w, c in zip(sub_scores, global_weights, global_criticalities)]
    final_norm = sum(w * c for w, c in zip(global_weights, global_criticalities))
    
    return sum(final_weighted) / max(final_norm, 0.001) * (1 - global_penalty)

def process_quantum_scoring(data, config, shots=1024):
    """
    Main quantum scoring interface.
    """
    if not QUANTUM_AVAILABLE:
        raise ImportError("Quantum backend not available. Install Qiskit.")
    
    normalized_data = normalize_data(data)
    blocks = []
    
    for block_config in config['blocks']:
        blocks.append({
            'values': normalized_data[block_config['name']],
            'weights': block_config['influence'],  # Business terminology
            'criticalities': block_config['priority'],
            'penalty': block_config.get('risk_adjustment', 0.0),
            'global_weight': block_config.get('block_influence', 1.0),
            'global_criticality': block_config.get('block_priority', 1.0),
            'lambdas': block_config.get('lambdas', []),
            'adjustments': block_config.get('adjustments', [])
        })
    
    return hierarchical_quantum_score(blocks, config.get('global_adjustment', 0.0), shots)

class Optimizer:
    """
    Quantum-native optimizer for hierarchical scoring.
    """
    def __init__(self, api_key=None, validate=False):
        self.api_key = api_key
        self.backend = 'simulator'  # Default quantum simulator
        
    def evaluate(self, data, config, backend='simulator', shots=1024):
        """
        Evaluate using quantum circuit simulation.
        
        Args:
            data: Dictionary with block names and values
            config: Configuration with blocks, influences, priorities
            backend: 'simulator' (included) or 'ibm_*' (requires qiskit-ibm-runtime)
            shots: Number of quantum measurements
        """
        if backend != 'simulator':
            raise ValueError(
                f"Backend '{backend}' requires qiskit-ibm-runtime. "
                "Install with: pip install qiskit-ibm-runtime"
            )
        
        return process_quantum_scoring(data, config, shots)


# values - datos
# weights - relevancia
# criticalities - impacto
# penalty - ajuste_riesgo
# global_weight - relevancia_bloque
# global_criticality - impacto_bloque
# process_credit_scoring - proceso_scoring
# Optimizer - Optimizador

