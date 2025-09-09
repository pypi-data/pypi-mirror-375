import logging

logger = logging.getLogger(__name__)

class ErrorHandler:
    def __init__(self, config):
        """
        Initializes the error handler.
        In a real application, this could be more complex,
        e.g., integrating with a service like Sentry or writing to a log file.
        """
        self.config = config
        logger.info("ErrorHandler initialized with a simple configuration.")

    def handle_exception(self, e: Exception, message: str = "An unexpected error occurred"):
        """
        A simple method to handle and log exceptions.
        """
        logger.error(f"{message}: {e}", exc_info=True)

