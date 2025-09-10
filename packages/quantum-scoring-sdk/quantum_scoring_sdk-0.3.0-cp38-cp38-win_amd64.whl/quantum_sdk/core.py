# quantum_sdk/core.py - v0.3.0 con IBM Hardware Support
import numpy as np
import math
from sklearn.preprocessing import MinMaxScaler

try:
    from qiskit import QuantumCircuit, transpile
    from qiskit.providers.aer import AerSimulator
    QUANTUM_AVAILABLE = True
except ImportError:
    QUANTUM_AVAILABLE = False

try:
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2 as Sampler
    from qiskit.transpiler.preset_passmanagers import generate_preset_pass_manager
    IBM_AVAILABLE = True
except ImportError:
    IBM_AVAILABLE = False

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

def clamp01(x):
    """Helper function from original IBM code"""
    return max(0.0, min(1.0, float(x)))

def count_ancilla_ones(counts, n_qubits, ancilla_index):
    """Helper from IBM implementation"""
    ones = 0
    total = 0
    for bitstring, cnt in counts.items():
        pos = len(bitstring) - 1 - ancilla_index
        if bitstring[pos] == '1':
            ones += cnt
        total += cnt
    return ones, total

def build_quantum_circuit(values, weights, criticalities, penalty=0.0):
    """Build quantum circuit - unified for simulator and IBM"""
    n = len(values)
    qc = QuantumCircuit(n + 1)
    
    # Normalize weights with criticalities (from IBM implementation)
    wc = np.array(weights) * np.array(criticalities)
    norm = wc.sum()
    if norm == 0:
        norm = 1.0
    probs = wc / norm
    
    # Encode values as rotations (IBM-tested logic)
    for i in range(n):
        s_eff = values[i] * (1.0 - penalty)
        angle = 2.0 * math.asin(math.sqrt(clamp01(s_eff * probs[i])))
        qc.ry(angle, i)
    
    # Weighted entanglement with ancilla
    anc = n
    for i in range(n):
        weight_angle = math.pi * probs[i]
        qc.cry(weight_angle, i, anc)
    
    qc.measure_all()
    return qc

def quantum_evaluate_simulator(values, weights, criticalities, penalty=0.0, shots=1024):
    """Evaluate using Aer simulator"""
    if not QUANTUM_AVAILABLE:
        raise ImportError("Qiskit not installed. Install with: pip install qiskit")
    
    qc = build_quantum_circuit(values, weights, criticalities, penalty)
    backend = AerSimulator()
    qc_transpiled = transpile(qc, backend)
    
    job = backend.run(qc_transpiled, shots=shots)
    result = job.result()
    counts = result.get_counts()
    
    # Process results (similar to IBM)
    ones, total = count_ancilla_ones(counts, len(values) + 1, len(values))
    score = ones / (total + 1e-12)
    
    # Entropy bonus
    if len(counts) > 1:
        probs = np.array(list(counts.values())) / total
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = min(np.log2(2**(len(values)+1)), np.log2(shots))
        entropy_factor = 1.0 + 0.1 * (entropy / (max_entropy + 1e-12))
        score = min(1.0, score * entropy_factor)
    
    return score

def quantum_evaluate_ibm(values, weights, criticalities, penalty=0.0, 
                        backend_service=None, backend_name='ibm_brisbane', shots=1024):
    """Evaluate using IBM Quantum - from proven implementation"""
    if not IBM_AVAILABLE:
        raise ImportError("Install qiskit-ibm-runtime to use IBM backends")
    
    if backend_service is None:
        raise ValueError("IBM backend service not configured. Use configure_ibm() first")
    
    # Get backend
    backend = backend_service.backend(backend_name)
    
    # Build circuit
    qc = build_quantum_circuit(values, weights, criticalities, penalty)
    
    # Transpile for IBM hardware
    pm = generate_preset_pass_manager(backend=backend, optimization_level=1)
    qc_transpiled = pm.run(qc)
    
    # Execute on IBM
    sampler = Sampler(mode=backend)
    job = sampler.run([qc_transpiled], shots=shots)
    result = job.result()
    
    # Process results
    counts = result[0].data.meas.get_counts()
    ones, total = count_ancilla_ones(counts, len(values) + 1, len(values))
    score = ones / (total + 1e-12)
    
    # Entropy adjustment from original
    if len(counts) > 1:
        probs = np.array(list(counts.values())) / total
        entropy = -np.sum(probs * np.log2(probs + 1e-10))
        max_entropy = np.log2(min(2**(len(values)+1), shots))
        entropy_factor = 1.0 + 0.1 * (entropy / max_entropy)
        score = min(1.0, score * entropy_factor)
    
    return score

def hierarchical_quantum_score(blocks, global_penalty=0.0, backend='simulator', 
                              ibm_service=None, ibm_backend='ibm_brisbane', shots=1024):
    """Hierarchical scoring with backend selection"""
    sub_scores = []
    global_weights = []
    global_criticalities = []
    
    for i, block in enumerate(blocks):
        # Apply non-linear adjustments if provided
        values = block['values']
        if block.get('lambdas') and block.get('adjustments'):
            values = [
                apply_non_linear(v, block['adjustments'][i], block['lambdas'])
                for i, v in enumerate(values)
            ]
        
        # Select backend and evaluate
        if backend == 'simulator':
            score = quantum_evaluate_simulator(
                values, block['weights'], block['criticalities'],
                block.get('penalty', 0.0), shots
            )
        elif backend.startswith('ibm'):
            score = quantum_evaluate_ibm(
                values, block['weights'], block['criticalities'],
                block.get('penalty', 0.0), ibm_service, backend, shots
            )
        else:
            raise ValueError(f"Unknown backend: {backend}")
        
        sub_scores.append(score)
        global_weights.append(block.get('global_weight', 1.0))
        global_criticalities.append(block.get('global_criticality', 1.0))
    
    # Aggregate scores
    final_weighted = [s * w * c for s, w, c in zip(sub_scores, global_weights, global_criticalities)]
    final_norm = sum(w * c for w, c in zip(global_weights, global_criticalities))
    
    return sum(final_weighted) / max(final_norm, 0.001) * (1 - global_penalty)

def process_quantum_scoring(data, config, backend='simulator', ibm_service=None, 
                           ibm_backend='ibm_brisbane', shots=1024):
    """Main quantum scoring interface"""
    if not QUANTUM_AVAILABLE:
        raise ImportError("Quantum backend not available. Install Qiskit.")
    
    normalized_data = normalize_data(data)
    blocks = []
    
    for block_config in config['blocks']:
        blocks.append({
            'values': normalized_data[block_config['name']],
            'weights': block_config['influence'],
            'criticalities': block_config['priority'],
            'penalty': block_config.get('risk_adjustment', 0.0),
            'global_weight': block_config.get('block_influence', 1.0),
            'global_criticality': block_config.get('block_priority', 1.0),
            'lambdas': block_config.get('lambdas', []),
            'adjustments': block_config.get('adjustments', [])
        })
    
    return hierarchical_quantum_score(
        blocks, config.get('global_adjustment', 0.0),
        backend, ibm_service, ibm_backend, shots
    )

class Optimizer:
    """Quantum-native optimizer with IBM support"""
    
    def __init__(self, api_key=None, validate=False):
        self.api_key = api_key
        self.ibm_service = None
        self.ibm_backend = 'ibm_brisbane'
        
    def configure_ibm(self, token, backend='ibm_brisbane', channel='ibm_quantum'):
        """Configure IBM Quantum access"""
        if not IBM_AVAILABLE:
            raise ImportError(
                "IBM Runtime not installed. "
                "Install with: pip install qiskit-ibm-runtime"
            )
        
        try:
            self.ibm_service = QiskitRuntimeService(
                channel=channel,
                token=token
            )
            # Verify backend exists
            available = [b.name for b in self.ibm_service.backends()]
            if backend not in available:
                raise ValueError(
                    f"Backend {backend} not available. "
                    f"Available: {available}"
                )
            self.ibm_backend = backend
            print(f"IBM Quantum configured successfully with {backend}")
            return True
        except Exception as e:
            raise ValueError(f"IBM configuration failed: {str(e)}")
    
    def evaluate(self, data, config, backend='simulator', shots=1024):
        """
        Evaluate using quantum circuit.
        
        Args:
            data: Dictionary with block names and values
            config: Configuration with blocks, influences, priorities
            backend: 'simulator' or 'ibm_brisbane', 'ibm_kyoto', etc.
            shots: Number of quantum measurements
        """
        if backend.startswith('ibm'):
            if not IBM_AVAILABLE:
                raise ImportError(
                    "IBM Runtime not installed. "
                    "Install with: pip install qiskit-ibm-runtime"
                )
            if self.ibm_service is None:
                raise ValueError(
                    "IBM not configured. First run: "
                    "opt.configure_ibm(token='YOUR_TOKEN')"
                )
            return process_quantum_scoring(
                data, config, backend, 
                self.ibm_service, backend, shots
            )
        else:
            # Use simulator
            return process_quantum_scoring(
                data, config, 'simulator', 
                None, None, shots
            )


# values - datos
# weights - relevancia
# criticalities - impacto
# penalty - ajuste_riesgo
# global_weight - relevancia_bloque
# global_criticality - impacto_bloque
# process_credit_scoring - proceso_scoring
# Optimizer - Optimizador

