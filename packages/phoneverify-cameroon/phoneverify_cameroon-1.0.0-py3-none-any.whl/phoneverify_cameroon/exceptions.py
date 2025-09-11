"""
Exceptions personnalisées pour la validation des numéros
"""


class PhoneValidationError(Exception):
    """Erreur de base pour la validation de numéros"""
    pass


class InvalidPhoneFormatError(PhoneValidationError):
    """Erreur de format de numéro invalide"""
    pass


class UnknownOperatorError(PhoneValidationError):
    """Erreur d'opérateur non reconnu"""
    pass


class EmptyPhoneNumberError(PhoneValidationError):
    """Erreur de numéro vide"""
    pass