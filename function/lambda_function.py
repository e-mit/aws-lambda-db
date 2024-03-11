import logging
import os
import json
from datetime import datetime

import psycopg2

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


def lambda_handler(event, context) -> None:

    timestamp = str(datetime.now())
    logger.debug(f'Event received at time: {timestamp}')
    logger.debug(f'Event data: {event}')

    try:
        for record in event['Records']:
            body = json.loads(record['body'])
            request_data = json.loads(body['responsePayload'])
            logger.debug(f"Request_data: {request_data}")
            logger.info("Intensity: "
                        f"{request_data['data'][0]['intensity']['actual']}")
    except Exception as e:
        logger.error(e)
        logger.info("Data extraction failed.")

    try:
        cursor.execute("INSERT INTO thetime VALUES (default, %s)",
                       (timestamp,))
        conn.commit()
        logger.info("DB OK.")
    except Exception as e:
        logger.error(e)
        conn.rollback()
        logger.info("DB rolled back.")
