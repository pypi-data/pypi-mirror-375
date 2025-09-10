import os
import logging

logger = logging.getLogger(__name__)

def create_dir_if_not_exists(directory):
    """Create a directory if it does not exist."""
    if not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
        except OSError as e:
            logger.error(f"Error creating directory {directory}: {e}")
            raise
