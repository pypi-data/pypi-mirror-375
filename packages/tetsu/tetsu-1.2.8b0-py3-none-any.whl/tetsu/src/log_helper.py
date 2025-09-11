import logging
import logging.config
import os
from datetime import datetime

import yaml


def setup_logging(config_path='config/logging.yaml'):
    """
    Initializes logging configuration for the entire application from a YAML file.
    This version adds a timestamp to the log filenames.

    This function should be called once when the application starts e.g. setup_logging()
    Then in every script (including the start script) you start the logger e.g. log = logging.getLogger("my_app")
    :param config_path: Path to the logging configuration YAML file.
    """
    if not os.path.exists(config_path):
        logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s: %(message)s")
        logging.warning(f"Logging config file not found at '{config_path}'. Using basic config.")
        return

    try:
        with open(config_path, 'rt') as f:
            config = yaml.safe_load(f.read())

        # Generate a single timestamp for all log files for this run
        timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

        # Iterate over handlers and update filenames with the timestamp
        for handler in config.get('handlers', {}).values():
            if 'filename' in handler:
                # Get the original filename
                original_filename = handler['filename']
                file_root, file_ext = os.path.splitext(original_filename)
                timed_filename = f"{file_root}_{timestamp}{file_ext}"
                handler['filename'] = timed_filename

                # Ensure the log directory exists
                log_dir = os.path.dirname(timed_filename)
                if log_dir:
                    os.makedirs(log_dir, exist_ok=True)

        logging.config.dictConfig(config)
        logging.info("Logging configured successfully from file.")

    except Exception as e:
        logging.basicConfig(level=logging.ERROR, format="%(asctime)s %(levelname)s: %(message)s")
        logging.error(f"Error configuring logging from '{config_path}': {e}", exc_info=True)
