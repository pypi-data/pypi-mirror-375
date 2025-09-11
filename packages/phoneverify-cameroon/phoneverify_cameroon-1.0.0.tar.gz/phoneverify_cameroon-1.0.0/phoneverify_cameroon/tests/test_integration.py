"""
Tests d'intégration complète du package
"""
import pytest
import phoneverify_cameroon as pv


class TestIntegration:
    """Tests d'intégration complets"""
    
    def test_complete_workflow_mtn(self):
        """Test workflow complet avec numéro MTN"""
        # Étape 1: Validation complète
        result = pv.validate_phone("+237 677 12 34 56")
        
        assert result['is_valid'] is True
        assert result['operator'] == 'MTN Mobile Money'
        assert result['operator_code'] == 'MTN'
        assert result['prefix'] == '677'
        assert result['cleaned_number'] == '677123456'
        assert result['original_input'] == '+237 677 12 34 56'
        
        # Étape 2: Vérification formats
        formats = result['formatted']
        assert formats['E164'] == '+237677123456'
        assert formats['national'] == '0677123456'
        assert formats['local'] == '677123456'
        assert formats['display'] == '677 12 34 56'
        
        # Étape 3: Détection opérateur seule
        operator = pv.detect_operator(result['cleaned_number'])
        assert operator == result['operator']
        
        # Étape 4: Formatage individuel
        e164 = pv.format_phone(result['cleaned_number'], 'E164')
        assert e164 == formats['E164']
    
    def test_complete_workflow_orange(self):
        """Test workflow complet avec numéro Orange"""
        result = pv.validate_phone("0655123456")
        
        assert result['is_valid'] is True
        assert result['operator'] == 'Orange Money'
        assert result['operator_code'] == 'ORG' 
        assert result['prefix'] == '655'
        
        # Vérifier cohérence avec détection séparée
        operator = pv.detect_operator("655123456")
        assert operator == result['operator']
    
    def test_mixed_batch_processing(self):
        """Test traitement en masse avec numéros mixtes"""
        test_numbers = [
            "677123456",      # MTN valide
            "+237655123456",  # Orange valide format international
            "0680123456",     # MTN valide format national
            "invalid123",     # Invalide
            "",               # Vide
            "123456789",      # Mauvais format
            "600123456",      # Préfixe inexistant
        ]
        
        # Test 1: Validation bulk
        validation_results = pv.bulk_validate(test_numbers)
        assert len(validation_results) == 7
        
        valid_count = sum(1 for r in validation_results if r['is_valid'])
        assert valid_count == 3  # Seulement les 3 premiers
        
        # Test 2: Détection bulk
        detection_results = pv.detect_operators_bulk(test_numbers)
        
        assert len(detection_results['MTN']) == 2  # 677 et 680
        assert len(detection_results['Orange']) == 1  # 655
        assert len(detection_results['Invalid']) >= 3  # Les invalides
        
        # Test 3: Conversion bulk
        conversion_results = pv.convert_format_bulk(test_numbers[:3], 'E164')
        
        assert conversion_results[0]['converted'] == '+237677123456'
        assert conversion_results[1]['converted'] == '+237655123456'
        assert conversion_results[2]['converted'] == '+237680123456'
    
    def test_all_operators_coverage(self):
        """Test couverture de tous les opérateurs supportés"""
        operators = pv.get_supported_operators()
        prefixes = pv.get_supported_prefixes()
        
        # Vérifier structure des opérateurs
        assert len(operators) == 2
        operator_codes = [op['code'] for op in operators]
        assert 'MTN' in operator_codes
        assert 'ORG' in operator_codes
        
        # Test au moins un préfixe de chaque opérateur
        mtn_op = next(op for op in operators if op['code'] == 'MTN')
        orange_op = next(op for op in operators if op['code'] == 'ORG')
        
        # Test préfixe MTN
        mtn_test_number = f"{mtn_op['prefixes'][0]}123456"
        result = pv.validate_phone(mtn_test_number)
        assert result['is_valid'] is True
        assert result['operator'] == mtn_op['name']
        
        # Test préfixe Orange  
        orange_test_number = f"{orange_op['prefixes'][0]}123456"
        result = pv.validate_phone(orange_test_number)
        assert result['is_valid'] is True
        assert result['operator'] == orange_op['name']
        
        # Vérifier cohérence préfixes
        all_operator_prefixes = []
        for op in operators:
            all_operator_prefixes.extend(op['prefixes'])
        
        assert set(all_operator_prefixes) == set(prefixes)
    
    def test_error_handling_consistency(self):
        """Test cohérence de gestion d'erreurs"""
        invalid_inputs = [
            "",               # Vide
            None,             # None
            "123",            # Trop court
            "12345678901",    # Trop long
            "abcdefghi",      # Lettres
            "987123456",      # Ne commence pas par 6
            "600123456",      # Préfixe inexistant
        ]
        
        for invalid_input in invalid_inputs:
            result = pv.validate_phone(invalid_input)
            
            # Toujours invalide
            assert result['is_valid'] is False
            assert result['error'] is not None
            assert isinstance(result['error'], str)
            assert len(result['error']) > 0
            
            # Opérateur toujours None pour invalides
            assert result['operator'] is None
            assert result['operator_code'] is None
            
            # Détection individuelle cohérente
            operator = pv.detect_operator(invalid_input or "")
            assert operator is None
    
    def test_package_metadata_consistency(self):
        """Test cohérence métadonnées du package"""
        # Vérifier présence des attributs
        assert hasattr(pv, '__version__')
        assert hasattr(pv, '__author__')
        assert hasattr(pv, '__description__')
        
        # Vérifier types
        assert isinstance(pv.__version__, str)
        assert isinstance(pv.__author__, str)
        assert isinstance(pv.__description__, str)
        
        # Vérifier valeurs non vides
        assert len(pv.__version__) > 0
        assert len(pv.__author__) > 0
        assert len(pv.__description__) > 0
        
        # Vérifier format version
        version_parts = pv.__version__.split('.')
        assert len(version_parts) >= 3  # x.y.z minimum
        
        for part in version_parts:
            assert part.isdigit(), f"Version part '{part}' should be numeric"
    
    def test_real_world_numbers(self):
        """Test avec des numéros réalistes camerounais"""
        # Numéros typiques qu'on peut voir en vrai
        real_world_cases = [
            # MTN formats variés
            ("677123456", True, "MTN"),
            ("0677123456", True, "MTN"), 
            ("+237677123456", True, "MTN"),
            ("+237 677 12 34 56", True, "MTN"),
            ("237-677-123-456", True, "MTN"),
            
            # Orange formats variés
            ("655987654", True, "Orange"),
            ("0655987654", True, "Orange"),
            ("+237655987654", True, "Orange"), 
            ("237 655 98 76 54", True, "Orange"),
            
            # Cas d'erreur communs
            ("77123456", False, None),     # Oubli du 6 initial
            ("6771234567", False, None),   # Chiffre en trop
            ("67712345", False, None),     # Chiffre en moins
        ]
        
        for number, should_be_valid, expected_operator in real_world_cases:
            result = pv.validate_phone(number)
            
            assert result['is_valid'] == should_be_valid, f"Failed for: {number}"
            
            if should_be_valid:
                assert expected_operator in result['operator'], f"Wrong operator for: {number}"
                
                # Vérifier que tous les formats sont cohérents
                formats = result['formatted']
                assert all(formats.values()), "All formats should be non-empty"
                
                # E164 doit commencer par +237
                assert formats['E164'].startswith('+237')
                
                # National doit commencer par 0
                assert formats['national'].startswith('0')
                
                # Local doit être 9 chiffres commençant par 6
                assert len(formats['local']) == 9
                assert formats['local'].startswith('6')
            else:
                assert result['operator'] is None
                assert result['error'] is not None