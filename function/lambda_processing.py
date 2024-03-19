from typing import Any
import logging

from sqlalchemy import Engine, URL
from sqlmodel import create_engine

import source_model
import sqs_event
import sql_model

logger = logging.getLogger()


def create_sql_engine(db_name: str, db_user: str | None, db_host: str | None,
                      db_port: str | int | None = None,
                      db_password: str | None = None,
                      db_dialect_driver: str = 'postgresql+psycopg2'
                      ) -> Engine:
    try:
        db_port_int = int(db_port)  # type: ignore
    except Exception:
        db_port_int = None

    if db_password == '':
        db_password = None
    if db_user == '':
        db_user = None
    if db_host == '':
        db_host = None

    url_object = URL.create(
        db_dialect_driver,
        username=db_user,
        password=db_password,
        host=db_host,
        database=db_name,
        port=db_port_int
    )
    return create_engine(url_object)


def lambda_processing(event: dict[str, Any], engine: Engine):
    try:
        for payload_dict in sqs_event.extract(event):
            source_api_data = source_model.validate_dict(payload_dict)
            logger.debug(f"Extracted data: {source_api_data}")
            sql_model.CarbonIntensityTable.add_from_source_model(
                engine, source_api_data.data[0])

    except Exception as e:
        logger.error("Event data extraction failed.")
        logger.error(e)
        logger.error(f'Event: {event}')
        raise e
