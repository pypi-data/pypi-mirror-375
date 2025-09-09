# quantum_sdk/core.py - NON-LINEAR + MINMAXSCALER (ENGLISH VERSION)
import numpy as np
from sklearn.preprocessing import MinMaxScaler


def normalize_data(data):
    """
    Normalize all input values using MinMaxScaler.
    data: dict with arrays/lists per block.
    """
    normalized = {}
    for key, values in data.items():
        values = np.array(values).reshape(-1, 1)
        scaler = MinMaxScaler(feature_range=(0, 1))
        normalized[key] = scaler.fit_transform(values).flatten().tolist()
    return normalized


def apply_non_linear(value, adjustments, lambdas):
    """
    Apply non-linear adjustments (secret sauce).
    """
    adjusted = value
    for adj, lam in zip(adjustments, lambdas):
        adjusted += lam * adj
    return max(0.0, min(1.0, adjusted))


def evaluate_block(values, weights, criticalities,
                   penalty=0.0, lambdas=None, adjustments=None):
    """
    Evaluate a single block using the non-linear formula.
    """
    if lambdas and adjustments:
        values = [
            apply_non_linear(v, adjustments[i], lambdas)
            for i, v in enumerate(values)
        ]

    weighted = [v * w * c for v, w, c in zip(values, weights, criticalities)]
    norm = sum(w * c for w, c in zip(weights, criticalities))
    score = sum(weighted) / max(norm, 0.001)
    return score * (1 - penalty)


def hierarchical_score(blocks, global_penalty=0.0):
    """
    Aggregate all block scores into a final score.
    """
    sub_scores = []
    global_weights = []
    global_criticalities = []

    for block in blocks:
        score = evaluate_block(
            block['values'],
            block['weights'],
            block['criticalities'],
            penalty=block.get('penalty', 0.0),
            lambdas=block.get('lambdas', []),
            adjustments=block.get('adjustments', [])
        )
        sub_scores.append(score)
        global_weights.append(block.get('global_weight', 1.0))
        global_criticalities.append(block.get('global_criticality', 1.0))

    final_weighted = [s * w * c for s, w, c in zip(sub_scores, global_weights, global_criticalities)]
    final_norm = sum(w * c for w, c in zip(global_weights, global_criticalities))

    return sum(final_weighted) / max(final_norm, 0.001) * (1 - global_penalty)


def process_credit_scoring(data, config):
    """
    Credit scoring interface using the non-linear formula.
    """
    normalized_data = normalize_data(data)

    blocks = []
    for block_config in config['blocks']:
        blocks.append({
            'values': normalized_data[block_config['name']],
            'weights': block_config['influence'],         # "influence" → weights
            'criticalities': block_config['priority'],    # "priority" → criticalities
            'penalty': block_config.get('risk_adjustment', 0.0),
            'global_weight': block_config.get('block_influence', 1.0),
            'global_criticality': block_config.get('block_priority', 1.0)
        })

    return hierarchical_score(blocks, config.get('global_adjustment', 0.0))


class Optimizer:
    """
    Public SDK class to evaluate different scoring modes.
    """
    def __init__(self, api_key=None):
        self.api_key = api_key

    def evaluate(self, data, config, mode="credit"):
        if mode == "credit":
            return process_credit_scoring(data, config)
        else:
            raise ValueError(f"Unsupported mode: {mode}")


# values - datos
# weights - relevancia
# criticalities - impacto
# penalty - ajuste_riesgo
# global_weight - relevancia_bloque
# global_criticality - impacto_bloque
# process_credit_scoring - proceso_scoring
# Optimizer - Optimizador

