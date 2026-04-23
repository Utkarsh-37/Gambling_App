class ValidationException(Exception):
    def __init__(self, message: str, field: str = None, attempted_value: any = None):
        super().__init__(message)
        self.field = field
        self.attempted_value = attempted_value

class DatabaseOperationException(Exception):
    pass