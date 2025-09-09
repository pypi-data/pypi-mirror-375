"""Exceptions for the synthbiodata package."""

class SynthBioDataError(Exception):
    """Base exception for all synthbiodata errors."""
    pass

class ConfigurationError(SynthBioDataError):
    """Raised when there is an error in the configuration."""
    pass

class ValidationError(ConfigurationError):
    """Raised when validation of configuration values fails."""
    pass

class RangeError(ValidationError):
    """Raised when a value is outside its allowed range."""
    def __init__(self, param: str, value: float, min_val: float | None = None, max_val: float | None = None):
        if min_val is not None and max_val is not None:
            message = f"{param} must be between {min_val} and {max_val}, got {value}"
        elif min_val is not None:
            message = f"{param} must be greater than {min_val}, got {value}"
        elif max_val is not None:
            message = f"{param} must be less than {max_val}, got {value}"
        else:
            message = f"Invalid value for {param}: {value}"
        super().__init__(message)

class DistributionError(ValidationError):
    """Raised when probability distributions are invalid."""
    pass

class DataTypeError(ConfigurationError):
    """Raised when an unsupported data type is specified."""
    pass
