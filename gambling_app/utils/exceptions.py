from enum import Enum

class ValidationErrorType(Enum):
    STAKE_ERROR = "STAKE_ERROR"
    BET_ERROR = "BET_ERROR"
    LIMIT_ERROR = "LIMIT_ERROR"
    PROBABILITY_ERROR = "PROBABILITY_ERROR"
    NUMERIC_ERROR = "NUMERIC_ERROR"
    RANGE_ERROR = "RANGE_ERROR"
    NULL_ERROR = "NULL_ERROR"

class ValidationException(Exception):
    """Base exception for validation tracking."""
    def __init__(self, message: str, error_type: ValidationErrorType = ValidationErrorType.NUMERIC_ERROR, 
                 field: str = None, attempted_value: any = None):
        super().__init__(message)
        self.error_type = error_type
        self.field = field
        self.attempted_value = attempted_value

class StakeValidationException(ValidationException):
    def __init__(self, message: str, field: str = None, attempted_value: any = None):
        super().__init__(message, ValidationErrorType.STAKE_ERROR, field, attempted_value)

class BetValidationException(ValidationException):
    def __init__(self, message: str, field: str = None, attempted_value: any = None):
        super().__init__(message, ValidationErrorType.BET_ERROR, field, attempted_value)

class LimitValidationException(ValidationException):
    def __init__(self, message: str, field: str = None, attempted_value: any = None):
        super().__init__(message, ValidationErrorType.LIMIT_ERROR, field, attempted_value)

class ProbabilityValidationException(ValidationException):
    def __init__(self, message: str, field: str = None, attempted_value: any = None):
        super().__init__(message, ValidationErrorType.PROBABILITY_ERROR, field, attempted_value)

class DatabaseOperationException(Exception):
    pass