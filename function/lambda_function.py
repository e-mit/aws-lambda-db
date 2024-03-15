import logging
import os
from typing import Any

from sqlmodel import SQLModel

import lambda_processing

logger = logging.getLogger()
logger.setLevel(os.environ['LOG_LEVEL'])

DB_USER = os.environ['DB_USER']
DB_NAME = os.environ['DB_NAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
DB_DIALECT_DRIVER = os.environ['DB_DIALECT_DRIVER']

logger.info("Connecting to database.")
engine = lambda_processing.create_sql_engine(DB_NAME, DB_USER, DB_HOST,
                                             DB_PORT, DB_PASSWORD,
                                             DB_DIALECT_DRIVER)
SQLModel.metadata.create_all(engine)


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    logger.debug(f'Event: {event}')
    lambda_processing.lambda_processing(event, engine)
