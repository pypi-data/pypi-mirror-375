"""
PhoneVerify Cameroon - Validation des numéros mobile money camerounais

API simple pour valider, détecter l'opérateur et convertir les formats
des numéros de téléphone mobile money du Cameroun (MTN et Orange).
"""

from .validator import PhoneNumberValidator, OperatorDetector, FormatConverter
from .models import Operator, OperatorRegistry, registry
from .exceptions import (
    PhoneValidationError,
    InvalidPhoneFormatError, 
    UnknownOperatorError,
    EmptyPhoneNumberError
)

__version__ = "1.0.0"
__author__ = "Djoko Christian"
__email__ = "contact@example.com"
__description__ = "Validation des numéros mobile money camerounais"

# Interface publique simplifiée
_validator = PhoneNumberValidator()
_detector = OperatorDetector()
_converter = FormatConverter()


def validate_phone(phone_number: str) -> dict:
    """
    Valide un numéro de téléphone camerounais
    
    Args:
        phone_number (str): Numéro à valider
        
    Returns:
        dict: Résultat de validation avec opérateur, formats, etc.
        
    Example:
        >>> validate_phone("677123456")
        {
            'original_input': '677123456',
            'is_valid': True,
            'operator': 'MTN Mobile Money',
            'operator_code': 'MTN',
            'prefix': '677',
            'cleaned_number': '677123456',
            'formatted': {
                'E164': '+237677123456',
                'national': '0677123456',
                'local': '677123456',
                'display': '677 12 34 56'
            },
            'error': None
        }
    """
    return _validator.validate(phone_number)


def detect_operator(phone_number: str) -> str:
    """
    Détecte l'opérateur d'un numéro
    
    Args:
        phone_number (str): Numéro à analyser
        
    Returns:
        str: Nom de l'opérateur ou None
        
    Example:
        >>> detect_operator("677123456")
        'MTN Mobile Money'
    """
    return _validator.detect_operator(phone_number)


def format_phone(phone_number: str, format_type: str = 'E164') -> str:
    """
    Formate un numéro selon le type demandé
    
    Args:
        phone_number (str): Numéro à formater
        format_type (str): Type de format ('E164', 'national', 'local', 'display')
        
    Returns:
        str: Numéro formaté
        
    Example:
        >>> format_phone("677123456", "E164")
        '+237677123456'
    """
    cleaned = _validator.clean_phone_number(phone_number)
    return _validator.format_number(cleaned, format_type)


def bulk_validate(phone_numbers: list) -> list:
    """
    Validation en masse de numéros
    
    Args:
        phone_numbers (list): Liste des numéros à valider
        
    Returns:
        list: Liste des résultats de validation
        
    Example:
        >>> bulk_validate(["677123456", "655123456"])
        [{'original_input': '677123456', 'is_valid': True, ...}, {...}]
    """
    return [validate_phone(phone) for phone in phone_numbers]


def detect_operators_bulk(phone_numbers: list) -> dict:
    """
    Détection d'opérateurs en masse avec regroupement
    
    Args:
        phone_numbers (list): Liste des numéros à analyser
        
    Returns:
        dict: Résultats regroupés par opérateur
        
    Example:
        >>> detect_operators_bulk(["677123456", "655123456"])
        {
            'MTN': [{'number': '677123456', 'prefix': '677', ...}],
            'Orange': [{'number': '655123456', 'prefix': '655', ...}],
            'Unknown': [],
            'Invalid': []
        }
    """
    return _detector.bulk_detect(phone_numbers)


def convert_format_bulk(phone_numbers: list, target_format: str = 'E164') -> list:
    """
    Conversion de formats en masse
    
    Args:
        phone_numbers (list): Liste des numéros à convertir
        target_format (str): Format cible
        
    Returns:
        list: Liste des numéros convertis
        
    Example:
        >>> convert_format_bulk(["677123456", "0655123456"], "E164")
        [
            {'original': '677123456', 'converted': '+237677123456', 'operator': 'MTN Mobile Money'},
            {'original': '0655123456', 'converted': '+237655123456', 'operator': 'Orange Money'}
        ]
    """
    return _converter.convert_batch(phone_numbers, target_format)


def get_supported_operators() -> list:
    """
    Retourne la liste des opérateurs supportés
    
    Returns:
        list: Liste des opérateurs avec leurs informations
        
    Example:
        >>> get_supported_operators()
        [
            {'code': 'MTN', 'name': 'MTN Mobile Money', 'prefixes': ['650', '651', ...]},
            {'code': 'ORG', 'name': 'Orange Money', 'prefixes': ['640', '655', ...]}
        ]
    """
    operators = registry.get_all_operators()
    return [
        {
            'code': op.code,
            'name': op.name,
            'prefixes': op.prefixes
        }
        for op in operators
    ]


def get_supported_prefixes() -> list:
    """
    Retourne tous les préfixes supportés
    
    Returns:
        list: Liste de tous les préfixes
        
    Example:
        >>> get_supported_prefixes()
        ['640', '650', '651', '655', ...]
    """
    return sorted(registry.get_all_prefixes())


# Interface pour compatibilité avancée
__all__ = [
    # Fonctions principales
    'validate_phone',
    'detect_operator', 
    'format_phone',
    'bulk_validate',
    'detect_operators_bulk',
    'convert_format_bulk',
    
    # Utilitaires
    'get_supported_operators',
    'get_supported_prefixes',
    
    # Classes avancées
    'PhoneNumberValidator',
    'OperatorDetector',
    'FormatConverter',
    'Operator',
    'OperatorRegistry',
    
    # Exceptions
    'PhoneValidationError',
    'InvalidPhoneFormatError',
    'UnknownOperatorError', 
    'EmptyPhoneNumberError',
    
    # Variables
    '__version__',
    '__author__',
    '__description__'
]