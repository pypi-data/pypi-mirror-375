"""
Tests pour les exceptions personnalisées
"""
import pytest
from phoneverify_cameroon.exceptions import (
    PhoneValidationError,
    InvalidPhoneFormatError,
    UnknownOperatorError,
    EmptyPhoneNumberError
)


class TestExceptions:
    
    def test_phone_validation_error(self):
        with pytest.raises(PhoneValidationError):
            raise PhoneValidationError("Test error")
    
    def test_invalid_phone_format_error(self):
        with pytest.raises(InvalidPhoneFormatError):
            raise InvalidPhoneFormatError("Format invalide")
        
        with pytest.raises(PhoneValidationError):
            raise InvalidPhoneFormatError("Format invalide")
    
    def test_unknown_operator_error(self):
        with pytest.raises(UnknownOperatorError):
            raise UnknownOperatorError("Opérateur inconnu")
        
        with pytest.raises(PhoneValidationError):
            raise UnknownOperatorError("Opérateur inconnu")
    
    def test_empty_phone_number_error(self):
        with pytest.raises(EmptyPhoneNumberError):
            raise EmptyPhoneNumberError("Numéro vide")
        
        with pytest.raises(PhoneValidationError):
            raise EmptyPhoneNumberError("Numéro vide")
    
    def test_exception_messages(self):
        try:
            raise InvalidPhoneFormatError("Message de test")
        except InvalidPhoneFormatError as e:
            assert str(e) == "Message de test"