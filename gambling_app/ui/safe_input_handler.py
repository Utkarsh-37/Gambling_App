from rich.console import Console
from rich.prompt import Prompt
from utils.input_validator import InputValidator
from repositories.validation_repository import ValidationRepository
from utils.exceptions import ValidationException

console = Console()

class SafeInputHandler:
    def __init__(self):
        self.validator = InputValidator()
        self.repo = ValidationRepository()

    def ask_float(self, prompt_text: str, field_name: str, gambler_id: int = None) -> float:
        """Continuously asks until a mathematically valid float is provided."""
        while True:
            raw_val = Prompt.ask(prompt_text)
            try:
                # 1. Catch NaN, Infinity, "pizza", empty strings
                dec_val = self.validator.parse_and_validate_numeric(raw_val, field_name)
                return float(dec_val)
            except ValidationException as ve:
                console.print(f"[bold red]✖ Invalid Input:[/bold red] {ve}")
                self.repo.log_event(ve.error_type.value, "WARNING", str(ve), ve.field, ve.attempted_value, gambler_id)

    def ask_probability(self, prompt_text: str, field_name: str = "probability") -> float:
        """Continuously asks until a valid 0.01 - 0.99 probability is provided."""
        while True:
            val = self.ask_float(prompt_text, field_name)
            try:
                self.validator.validate_probability(val)
                return val
            except ValidationException as ve:
                console.print(f"[bold red]✖ Invalid Probability:[/bold red] {ve}")
                self.repo.log_event(ve.error_type.value, "WARNING", str(ve), ve.field, ve.attempted_value)