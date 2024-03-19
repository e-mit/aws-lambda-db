"""Functions for implementing the lambda."""

from typing import Any
import logging
from dataclasses import dataclass

from sqlalchemy import Engine, URL
from sqlmodel import create_engine

import source_model
import sqs_event
import sql_model

logger = logging.getLogger()


@dataclass(kw_only=True)
class DatabaseSettings:
    """Gather database connection information and create engine."""

    db_name: str
    db_user: str | None
    db_host: str | None
    db_port: str | int | None = None
    db_password: str | None = None
    db_dialect_driver: str = 'postgresql+psycopg2'

    def create_sql_engine(self) -> Engine:
        """Create a sqlalchemy/sqlmodel Engine instance."""
        try:
            db_port_int = int(self.db_port)  # type: ignore
        except (TypeError, ValueError):
            db_port_int = None

        if self.db_password == '':  # nosec
            self.db_password = None
        if self.db_user == '':
            self.db_user = None
        if self.db_host == '':
            self.db_host = None

        url_object = URL.create(
            self.db_dialect_driver,
            username=self.db_user,
            password=self.db_password,
            host=self.db_host,
            database=self.db_name,
            port=db_port_int
        )
        return create_engine(url_object)


def lambda_processing(event: dict[str, Any], engine: Engine):
    """ETL: extract event data; validate; add to database."""
    try:
        for payload_dict in sqs_event.extract(event):
            source_api_data = source_model.validate_dict(payload_dict)
            logger.debug("Extracted data: %s", source_api_data)
            sql_model.CarbonIntensityTable.add_from_source_model(
                engine, source_api_data.data[0])

    except Exception as e:
        logger.error("Event data extraction failed.")
        logger.error(e)
        logger.error('Event: %s', event)
        raise e
