class TuneQError(Exception):
    """Base exception for TuneQ errors."""
    pass

class CalibrationError(TuneQError):
    """Raised when calibration routines fail."""
    pass

class OptimizationError(TuneQError):
    """Raised when circuit optimization fails."""
    pass
