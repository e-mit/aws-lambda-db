"""An AWS Lambda to transfer data from a AWS SQS queue to a database."""

import logging
import os
from typing import Any

from sqlmodel import SQLModel

import lambda_processing

logger = logging.getLogger()
logger.setLevel(os.environ['LOG_LEVEL'])

logger.info("Connecting to database.")
db_settings = lambda_processing.DatabaseSettings(
    db_user=os.environ['DB_USER'],
    db_name=os.environ['DB_NAME'],
    db_password=os.environ['DB_PASSWORD'],
    db_host=os.environ['DB_HOST'],
    db_port=os.environ['DB_PORT'],
    db_dialect_driver=os.environ['DB_DIALECT_DRIVER'])
engine = db_settings.create_sql_engine()
SQLModel.metadata.create_all(engine)


def lambda_handler(event: dict[str, Any], _context_unused: Any) -> None:
    """Define the lambda function."""
    logger.debug('Event: %s', event)
    lambda_processing.lambda_processing(event, engine)
