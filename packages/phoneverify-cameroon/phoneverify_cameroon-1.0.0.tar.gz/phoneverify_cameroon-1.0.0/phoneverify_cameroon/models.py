"""
Modèles de données pour la validation des numéros camerounais
"""
from dataclasses import dataclass
from typing import List, Optional
import json
import os


@dataclass
class Operator:
    """Représente un opérateur mobile money"""
    code: str
    name: str
    prefixes: List[str]


class OperatorRegistry:
    """Gestionnaire des opérateurs et préfixes"""
    
    def __init__(self):
        self._operators = {}
        self._prefix_to_operator = {}
        self._load_data()
    
    def _load_data(self):
        """Charge les données depuis le fichier JSON"""
        data_file = os.path.join(os.path.dirname(__file__), 'data', 'operators.json')
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        for operator_name, operator_data in data.items():
            operator = Operator(
                code=operator_data['code'],
                name=operator_data['name'],
                prefixes=operator_data['prefixes']
            )
            self._operators[operator_name] = operator
            
            # Index préfixe -> opérateur pour recherche rapide
            for prefix in operator.prefixes:
                self._prefix_to_operator[prefix] = operator
    
    def get_operator_by_prefix(self, prefix: str) -> Optional[Operator]:
        """Retourne l'opérateur pour un préfixe donné"""
        return self._prefix_to_operator.get(prefix)
    
    def get_all_operators(self) -> List[Operator]:
        """Retourne tous les opérateurs"""
        return list(self._operators.values())
    
    def get_all_prefixes(self) -> List[str]:
        """Retourne tous les préfixes actifs"""
        return list(self._prefix_to_operator.keys())


# Instance globale
registry = OperatorRegistry()