"""
Tests pour les modèles de données
"""
import pytest
from phoneverify_cameroon.models import Operator, OperatorRegistry, registry


class TestOperator:    
    def test_operator_creation(self):
        operator = Operator(
            code="TEST",
            name="Test Operator", 
            prefixes=["123", "456"]
        )
        assert operator.code == "TEST"
        assert operator.name == "Test Operator"
        assert operator.prefixes == ["123", "456"]


class TestOperatorRegistry:
    """Tests pour le registre des opérateurs"""
    
    def test_registry_initialization(self):
        assert len(registry.get_all_operators()) == 2
        
        operators = {op.code: op for op in registry.get_all_operators()}
        assert "MTN" in operators
        assert "ORG" in operators
    
    def test_get_operator_by_prefix(self):
        mtn_operator = registry.get_operator_by_prefix("677")
        assert mtn_operator is not None
        assert mtn_operator.code == "MTN"
        assert mtn_operator.name == "MTN Mobile Money"
        
        orange_operator = registry.get_operator_by_prefix("655")
        assert orange_operator is not None
        assert orange_operator.code == "ORG"
        assert orange_operator.name == "Orange Money"
        
        unknown = registry.get_operator_by_prefix("999")
        assert unknown is None
    
    def test_get_all_prefixes(self):
        prefixes = registry.get_all_prefixes()
        assert isinstance(prefixes, list)
        assert len(prefixes) > 30  # Au moins 33 préfixes
        assert "677" in prefixes  # MTN
        assert "655" in prefixes  # Orange
        assert "640" in prefixes  # Orange
    
    def test_mtn_prefixes(self):
        mtn_operator = registry.get_operator_by_prefix("677")
        expected_mtn_prefixes = [
            '650', '651', '652', '653', '654',
            '670', '671', '672', '673', '674', '675', '676', '677', '678', '679',
            '680', '681', '682', '683'
        ]
        
        assert set(expected_mtn_prefixes).issubset(set(mtn_operator.prefixes))
    
    def test_orange_prefixes(self):
        orange_operator = registry.get_operator_by_prefix("655")
        expected_orange_prefixes = [
            '640', '655', '656', '657', '658', '659',
            '686', '687', '688', '689',
            '690', '691', '692', '693', '694', '695', '696', '697', '698', '699'
        ]
        
        assert set(expected_orange_prefixes).issubset(set(orange_operator.prefixes))