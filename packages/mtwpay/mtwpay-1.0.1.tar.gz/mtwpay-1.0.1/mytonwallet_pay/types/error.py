class APIError(Exception):
    """MyTonWallet Pay API Error"""
    def __init__(self, message: str, code: int | None = None):
        super().__init__(message)
        self.code = code
        self.message = message

    def __str__(self):
        if self.code is not None:
            return f"APIError {self.code}: {self.message}"
        return self.message
