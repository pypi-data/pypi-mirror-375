"""
Validation des numéros de téléphone mobile money camerounais
"""
import re
from typing import Dict, List, Optional
from .models import registry


class PhoneNumberValidator:
    """Validateur principal pour les numéros camerounais"""
    
    def __init__(self):
        self.cameroon_patterns = {
            'local': r'^6\d{8}$',           
            'national': r'^0?6\d{8}$',     
            'international': r'^\+?237\s?6\d{8}$'
        }
    
    def clean_phone_number(self, phone_number: str) -> str:
        """Nettoie un numéro de téléphone"""
        if not phone_number:
            return ""
        
        cleaned = re.sub(r'[\s\-\.\(\)]', '', str(phone_number))
        
        if cleaned.startswith('+237'):
            cleaned = cleaned[4:]
        elif cleaned.startswith('237'):
            cleaned = cleaned[3:]
        elif cleaned.startswith('0'):
            cleaned = cleaned[1:]
        
        return cleaned
    
    def is_valid_format(self, phone_number: str) -> Dict:
        """Vérifie le format d'un numéro"""
        if not phone_number:
            return {
                'is_valid': False, 
                'format_type': None, 
                'error': 'Numero vide'
            }
        
        if len(phone_number) != 9:
            return {
                'is_valid': False,
                'format_type': None,
                'error': f'Longueur incorrecte: {len(phone_number)} chiffres (9 attendus)'
            }
        
        if not phone_number.isdigit():
            return {
                'is_valid': False,
                'format_type': None,
                'error': 'Le numero doit contenir uniquement des chiffres'
            }
        
        if not phone_number.startswith('6'):
            return {
                'is_valid': False,
                'format_type': None,
                'error': 'Les numeros mobiles camerounais commencent par 6'
            }
        
        return {
            'is_valid': True,
            'format_type': 'local',
            'error': None
        }
    
    def detect_operator(self, phone_number: str) -> Optional[str]:
        """Détecte l'opérateur d'un numéro"""
        if not phone_number or len(phone_number) < 3:
            return None
        
        prefix = phone_number[:3]
        operator = registry.get_operator_by_prefix(prefix)
        return operator.name if operator else None
    
    def format_number(self, phone_number: str, format_type: str = 'E164') -> str:
        """Formate un numéro selon le type demandé"""
        if not phone_number:
            return ""
        
        if format_type == 'E164':
            return f"+237{phone_number}"
        elif format_type == 'national':
            return f"0{phone_number}"
        elif format_type == 'local':
            return phone_number
        elif format_type == 'display':
            return f"{phone_number[:3]} {phone_number[3:5]} {phone_number[5:7]} {phone_number[7:9]}"
        else:
            return phone_number
    
    def validate(self, phone_number: str) -> Dict:
        """Validation complète d'un numéro"""
        result = {
            'original_input': phone_number,
            'is_valid': False,
            'operator': None,
            'operator_code': None,
            'prefix': None,
            'cleaned_number': None,
            'formatted': {},
            'error': None
        }
        
        cleaned = self.clean_phone_number(phone_number)
        result['cleaned_number'] = cleaned
        
        if not cleaned:
            result['error'] = 'Numero vide apres nettoyage'
            return result
        
        format_check = self.is_valid_format(cleaned)
        if not format_check['is_valid']:
            result['error'] = format_check['error']
            return result
        
        prefix = cleaned[:3]
        operator = registry.get_operator_by_prefix(prefix)
        if not operator:
            result['error'] = f"Prefixe {prefix} non reconnu ou inactif"
            return result
        
        result['prefix'] = prefix
        result['operator'] = operator.name
        result['operator_code'] = operator.code
        
        result['formatted'] = {
            'E164': self.format_number(cleaned, 'E164'),
            'national': self.format_number(cleaned, 'national'),
            'local': self.format_number(cleaned, 'local'),
            'display': self.format_number(cleaned, 'display')
        }
        
        result['is_valid'] = True
        result['error'] = None
        
        return result


class OperatorDetector:
    """Détection d'opérateurs en masse"""
    
    def __init__(self):
        self.validator = PhoneNumberValidator()
    
    def bulk_detect(self, phone_numbers: List[str]) -> Dict:
        """Détection en masse avec regroupement par opérateur"""
        results = {
            'MTN': [],
            'Orange': [],
            'Unknown': [],
            'Invalid': []
        }
        
        for phone in phone_numbers:
            validation = self.validator.validate(phone)
            
            if not validation['is_valid']:
                results['Invalid'].append({
                    'number': phone,
                    'error': validation['error']
                })
            elif validation['operator']:
                # Utilise le nom de l'opérateur pour le regroupement
                operator_key = 'MTN' if 'MTN' in validation['operator'] else 'Orange'
                results[operator_key].append({
                    'number': phone,
                    'prefix': validation['prefix'],
                    'formatted': validation['formatted']['E164']
                })
            else:
                results['Unknown'].append({
                    'number': phone,
                    'prefix': validation.get('prefix')
                })
        
        return results


class FormatConverter:
    """Conversion de formats de numéros"""
    
    def __init__(self):
        self.validator = PhoneNumberValidator()
    
    def convert_batch(self, phone_numbers: List[str], target_format: str = 'E164') -> List[Dict]:
        """Conversion en masse vers un format spécifique"""
        results = []
        
        for phone in phone_numbers:
            validation = self.validator.validate(phone)
            
            if validation['is_valid']:
                results.append({
                    'original': phone,
                    'converted': validation['formatted'][target_format],
                    'operator': validation['operator']
                })
            else:
                results.append({
                    'original': phone,
                    'converted': None,
                    'error': validation['error']
                })
        
        return results