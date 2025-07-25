class NotFoundError(Exception):
    """
    Custom error class for handling not found errors.

    Args:
        message (str): The error message to display.
    """

    def __init__(self, message: str):
        super().__init__(message)
        self.message = message
