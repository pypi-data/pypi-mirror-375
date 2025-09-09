# quantum_sdk/__init__.py
import requests
from .core import process_credit_scoring, hierarchical_score

class Optimizer:
    def __init__(self, api_key=None, validate=False):
        self.api_key = api_key
        if validate and api_key:
            self.validate_key()
    
    def validate_key(self):
        # Por ahora skip, activar cuando esté listo
        pass
    
    def evaluate(self, data, config, mode='credit'):
        if mode == 'credit':
            return process_credit_scoring(data, config)
        else:
            # Modo genérico
            return hierarchical_score(config['blocks'])
