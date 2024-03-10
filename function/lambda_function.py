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

logger = logging.getLogger()
logger.setLevel(logging.INFO)

logger.info("Connecting to database.")
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
                        host=DB_HOST, port=DB_PORT)
cursor = conn.cursor()


def lambda_handler(event, context):

    timestamp = str(datetime.now())
    logger.info(f'Event received at time: {timestamp}')
    logger.info(f'Event data: {event}')

    try:
        for record in event['Records']:
            body = json.loads(record['body'])
            request_data = json.loads(body['responsePayload'])
            logger.info(f"Request_data: {request_data}")
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
