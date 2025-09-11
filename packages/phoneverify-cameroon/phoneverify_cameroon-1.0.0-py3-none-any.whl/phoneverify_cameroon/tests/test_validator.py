"""
Tests pour le validateur de numéros camerounais
"""
import pytest
from phoneverify_cameroon import (
    validate_phone, 
    detect_operator,
    format_phone,
    bulk_validate,
    get_supported_operators,
    get_supported_prefixes
)


class TestPhoneValidation:
    """Tests de validation de numéros"""
    
    def test_valid_mtn_number(self):
        """Test numéro MTN valide"""
        result = validate_phone("677123456")
        assert result['is_valid'] is True
        assert result['operator'] == 'MTN Mobile Money'
        assert result['operator_code'] == 'MTN'
        assert result['prefix'] == '677'
        assert result['formatted']['E164'] == '+237677123456'
    
    def test_valid_orange_number(self):
        """Test numéro Orange valide"""
        result = validate_phone("655123456")
        assert result['is_valid'] is True
        assert result['operator'] == 'Orange Money'
        assert result['operator_code'] == 'ORG'
        assert result['prefix'] == '655'
    
    def test_invalid_format(self):
        """Test format invalide"""
        result = validate_phone("123456789")
        assert result['is_valid'] is False
        assert result['error'] is not None
        assert "commencent par 6" in result['error']
    
    def test_wrong_length(self):
        """Test longueur incorrecte"""
        result = validate_phone("67712345")  # 8 chiffres au lieu de 9
        assert result['is_valid'] is False
        assert "Longueur incorrecte" in result['error']
    
    def test_empty_number(self):
        """Test numéro vide"""
        result = validate_phone("")
        assert result['is_valid'] is False
        assert "vide" in result['error']
    
    def test_international_format(self):
        """Test format international"""
        result = validate_phone("+237 677 12 34 56")
        assert result['is_valid'] is True
        assert result['cleaned_number'] == '677123456'
        assert result['operator'] == 'MTN Mobile Money'
    
    def test_national_format(self):
        """Test format national"""
        result = validate_phone("0677123456")
        assert result['is_valid'] is True
        assert result['cleaned_number'] == '677123456'


class TestOperatorDetection:
    """Tests de détection d'opérateurs"""
    
    def test_detect_mtn(self):
        """Test détection MTN"""
        operator = detect_operator("677123456")
        assert operator == 'MTN Mobile Money'
    
    def test_detect_orange(self):
        """Test détection Orange"""
        operator = detect_operator("655123456")
        assert operator == 'Orange Money'
    
    def test_detect_unknown(self):
        """Test préfixe inconnu"""
        operator = detect_operator("600123456")  # Préfixe inexistant
        assert operator is None


class TestFormatting:
    """Tests de formatage"""
    
    def test_e164_format(self):
        """Test format E164"""
        formatted = format_phone("677123456", "E164")
        assert formatted == '+237677123456'
    
    def test_national_format(self):
        """Test format national"""
        formatted = format_phone("677123456", "national")
        assert formatted == '0677123456'
    
    def test_display_format(self):
        """Test format d'affichage"""
        formatted = format_phone("677123456", "display")
        assert formatted == '677 12 34 56'


class TestBulkOperations:
    """Tests des opérations en masse"""
    
    def test_bulk_validate(self):
        """Test validation en masse"""
        numbers = ["677123456", "655123456", "invalid123"]
        results = bulk_validate(numbers)
        
        assert len(results) == 3
        assert results[0]['is_valid'] is True  # MTN
        assert results[1]['is_valid'] is True  # Orange  
        assert results[2]['is_valid'] is False # Invalid


class TestUtilities:
    """Tests des utilitaires"""
    
    def test_supported_operators(self):
        """Test liste des opérateurs"""
        operators = get_supported_operators()
        assert len(operators) == 2
        
        mtn = next(op for op in operators if op['code'] == 'MTN')
        assert mtn['name'] == 'MTN Mobile Money'
        assert '677' in mtn['prefixes']
    
    def test_supported_prefixes(self):
        """Test liste des préfixes"""
        prefixes = get_supported_prefixes()
        assert isinstance(prefixes, list)
        assert '677' in prefixes  # MTN
        assert '655' in prefixes  # Orange
        assert len(prefixes) > 30  # Au moins 33 préfixes


if __name__ == '__main__':
    pytest.main([__file__])