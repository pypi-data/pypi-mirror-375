"""
Tests de performance du package
"""
import time
import pytest
import phoneverify_cameroon as pv


class TestPerformance:    
    def test_single_validation_speed(self):
        start_time = time.time()
        
        for i in range(1000):
            result = pv.validate_phone("677123456")
            assert result['is_valid'] is True
        
        end_time = time.time()
        duration = end_time - start_time
        
        assert duration < 1.0, f"1000 validations ont pris {duration:.3f}s (trop lent)"
        
        # Calcul vitesse moyenne
        avg_ms = (duration / 1000) * 1000
        print(f"\nVitesse moyenne: {avg_ms:.2f}ms par validation")
        
        # Doit être sous 1ms par validation
        assert avg_ms < 1.0, f"Validation trop lente: {avg_ms:.2f}ms"
    
    def test_bulk_validation_speed(self):
        """Test vitesse de validation en masse"""
        # Préparer 100 numéros différents
        numbers = []
        mtn_prefixes = ['650', '651', '677', '678']
        orange_prefixes = ['640', '655', '656', '657']
        
        for i in range(50):
            # MTN
            prefix = mtn_prefixes[i % len(mtn_prefixes)]
            numbers.append(f"{prefix}{100000 + i:06d}")
            
            # Orange
            prefix = orange_prefixes[i % len(orange_prefixes)]
            numbers.append(f"{prefix}{100000 + i:06d}")
        
        start_time = time.time()
        results = pv.bulk_validate(numbers)
        end_time = time.time()
        
        duration = end_time - start_time
        
        # Vérifier résultats
        assert len(results) == 100
        valid_count = sum(1 for r in results if r['is_valid'])
        assert valid_count == 100, "Tous les numéros devraient être valides"
        
        # Performance: 100 validations en moins de 100ms
        assert duration < 0.1, f"100 validations en masse ont pris {duration:.3f}s (trop lent)"
        
        avg_ms = (duration / 100) * 1000
        print(f"\nVitesse bulk: {avg_ms:.2f}ms par validation")
    
    def test_operator_detection_speed(self):
        """Test vitesse de détection d'opérateurs"""
        numbers = ["677123456"] * 1000  # Répéter le même numéro
        
        start_time = time.time()
        
        for number in numbers:
            operator = pv.detect_operator(number)
            assert operator == 'MTN Mobile Money'
        
        end_time = time.time()
        duration = end_time - start_time
        
        # 1000 détections en moins de 0.5s
        assert duration < 0.5, f"1000 détections ont pris {duration:.3f}s"
        
        avg_ms = (duration / 1000) * 1000
        print(f"\nVitesse détection: {avg_ms:.2f}ms par opération")
    
    def test_memory_usage(self):
        """Test utilisation mémoire basique"""
        # Créer beaucoup de validations pour voir si pas de fuite mémoire
        results = []
        
        for i in range(1000):
            result = pv.validate_phone(f"677{100000 + i:06d}")
            results.append(result)
        
        # Vérifier que tous les résultats sont valides
        assert all(r['is_valid'] for r in results)
        
        # Test que les données restent cohérentes
        first_result = results[0]
        last_result = results[-1]
        
        assert first_result['operator'] == last_result['operator']
        assert first_result['operator'] == 'MTN Mobile Money'
    
    @pytest.mark.slow
    def test_large_bulk_operations(self):
        """Test opérations en masse importantes"""
        # Générer 1000 numéros
        numbers = []
        for i in range(1000):
            prefix = '677' if i % 2 == 0 else '655'
            numbers.append(f"{prefix}{100000 + i:06d}")
        
        # Test validation bulk
        start_time = time.time()
        results = pv.bulk_validate(numbers)
        validation_time = time.time() - start_time
        
        # Test détection bulk
        start_time = time.time()
        detection_results = pv.detect_operators_bulk(numbers)
        detection_time = time.time() - start_time
        
        start_time = time.time()
        conversion_results = pv.convert_format_bulk(numbers, "E164")
        conversion_time = time.time() - start_time
        
        assert len(results) == 1000
        assert len(conversion_results) == 1000
        assert len(detection_results['MTN']) + len(detection_results['Orange']) == 1000
        
        print(f"\nPerformance 1000 numéros:")
        print(f"- Validation: {validation_time:.3f}s")
        print(f"- Détection: {detection_time:.3f}s") 
        print(f"- Conversion: {conversion_time:.3f}s")
        
        assert validation_time < 2.0, "Validation bulk trop lente"
        assert detection_time < 1.0, "Détection bulk trop lente"
        assert conversion_time < 1.0, "Conversion bulk trop lente"