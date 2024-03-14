from typing import Any
import logging

from sqlalchemy import Engine

import model
import sqs_event
from function import sql_model

logger = logging.getLogger()


def lambda_processing(event: dict[str, Any], engine: Engine):
    try:
        for payload_dict in sqs_event.extract(event):
            source_api_data = model.validate_dict(payload_dict)
            logger.debug(f"Extracted data: {source_api_data}")
            sql_model.CarbonIntensityTable.add_from_source_model(
                engine, source_api_data.data[0])

    except Exception as e:
        logger.info("Event data extraction failed.")
        logger.error(e)
        raise e
