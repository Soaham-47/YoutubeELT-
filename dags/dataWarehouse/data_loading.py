import logging
import json
from datetime import date

logger = logging.getLogger(__name__)

def load_data():
    path=f"./data/YT_data_{date.today()}.json"
    try:
        logger.info(f"Loading data from {path}")
        with open(path, 'r', encoding='utf-8') as raw_data_file:
            data = json.load(raw_data_file)
        return data
    except FileNotFoundError:
        logger.error(f"File not found: {path}")
        raise
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {path}")
        raise
