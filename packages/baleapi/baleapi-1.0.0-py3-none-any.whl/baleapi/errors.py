class BaleError(Exception):
    """Base class for all Bale API errors"""
    pass

class BaleAPIError(BaleError):
    """Raised when API returns an error response"""
    def __init__(self, code, description):
        self.code = code
        self.description = description
        super().__init__(f"[{code}] {description}")
