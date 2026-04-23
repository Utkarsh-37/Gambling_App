import math
from decimal import Decimal, InvalidOperation
from dataclasses import dataclass
from typing import List, Tuple
from utils.exceptions import (
    ValidationErrorType, ValidationException, StakeValidationException, 
    BetValidationException, LimitValidationException, ProbabilityValidationException
)

@dataclass
class ValidationConfig:
    strict_mode: bool = True
    allow_zero_stake: bool = False
    min_probability: float = 0.01
    max_probability: float = 0.99

class InputValidator:
    def __init__(self):
        self.config = ValidationConfig()

    def parse_and_validate_numeric(self, value: str, field_name: str) -> Decimal:
        """Gracefully handles strings, nulls, NaN, and Infinity."""
        if value is None or str(value).strip() == "":
            raise ValidationException("Input cannot be empty.", ValidationErrorType.NULL_ERROR, field_name, value)
        try:
            val_float = float(value)
            if math.isnan(val_float) or math.isinf(val_float):
                raise ValidationException("Input cannot be NaN or Infinity.", ValidationErrorType.NUMERIC_ERROR, field_name, value)
            return Decimal(str(value))
        except (ValueError, InvalidOperation):
            raise ValidationException("Input must be a valid number.", ValidationErrorType.NUMERIC_ERROR, field_name, value)

    def validate_initial_stake(self, stake: Decimal, min_allowed: Decimal, max_allowed: Decimal) -> bool:
        if stake < 0:
            raise StakeValidationException("Stake cannot be negative.", "initial_stake", stake)
        if stake == 0 and not self.config.allow_zero_stake:
            raise StakeValidationException("Stake cannot be zero.", "initial_stake", stake)
        if stake < min_allowed or stake > max_allowed:
            raise StakeValidationException(f"Stake must be between {min_allowed} and {max_allowed}.", "initial_stake", stake)
        return True

    def validate_limits(self, lower_limit: Decimal, upper_limit: Decimal, initial_stake: Decimal):
        if lower_limit < 0:
            raise LimitValidationException("Loss limit cannot be negative.", "lower_limit", lower_limit)
        if upper_limit <= lower_limit:
            raise LimitValidationException("Win threshold must be strictly greater than loss threshold.", "upper_limit", upper_limit)
        if initial_stake <= lower_limit or initial_stake >= upper_limit:
            raise LimitValidationException("Initial stake must be strictly between loss and win thresholds.", "limits", initial_stake)
        return True

    def validate_probability(self, prob: float):
        if prob < self.config.min_probability or prob > self.config.max_probability:
            raise ProbabilityValidationException(f"Probability must be between {self.config.min_probability} and {self.config.max_probability}.", "win_probability", prob)
        return True