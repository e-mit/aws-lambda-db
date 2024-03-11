import logging
import os
from typing import Any

import psycopg2

import model
import event_data

DB_USER = os.environ['DB_USER']
DB_NAME = os.environ['DB_NAME']
DB_PASSWORD = os.environ['DB_PASSWORD']
DB_HOST = os.environ['DB_HOST']
DB_PORT = os.environ['DB_PORT']
LOG_LEVEL = os.environ['LOG_LEVEL']

logger = logging.getLogger()
logger.setLevel(LOG_LEVEL)

logger.info("Connecting to database.")
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
                        host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()


def lambda_handler(event: dict[str, Any], context: Any) -> None:
    logger.debug(f'Event: {event}')

    try:
        for payload in event_data.extract(event):
            data_object = model.validate_dict(payload)
            logger.debug(f"Extracted data: {data_object}")
    except Exception as e:
        logger.error(e)
        logger.info("Data extraction failed.")

    try:
        cursor.execute("INSERT INTO thetime VALUES (default, %s)",
                       (4,))
        conn.commit()
        logger.info("DB OK.")
    except Exception as e:
        logger.error(e)
        conn.rollback()
        logger.info("DB rolled back.")
