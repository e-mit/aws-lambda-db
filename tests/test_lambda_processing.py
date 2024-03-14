import unittest
import sys
import json
import logging
import os
from typing import Any

from sqlmodel import select, create_engine, SQLModel
from sqlalchemy import Engine
import pydantic

logging.getLogger().setLevel("CRITICAL")
sys.path.append("function")

from function import lambda_processing, sql_model  # noqa
from sqlite_helper import SQLiteHelper, PSQLHelper, DBhelper  # noqa


class TestLambdaProcessing(unittest.TestCase):

    def make_engine(self) -> Engine:
        """Create the SQLAlchemy engine."""
        raise NotImplementedError("ABC")

    def prepare_database(self) -> DBhelper:
        """Set up a test database to use."""
        print()
        print(f"Skipping test of abstract class {type(self).__name__}.")
        self.skipTest("ABC")

    def get_test_event_data(self) -> dict[str, Any]:
        with open('tests/test_sqs_event.json') as file:
            return json.load(file)

    def setUp(self) -> None:
        self.test_event = self.get_test_event_data()
        self.db = self.prepare_database()
        self.engine = self.make_engine()
        SQLModel.metadata.create_all(self.engine)
        lambda_processing.lambda_processing(self.test_event,
                                            self.engine)
        return super().setUp()

    def test_table_exists(self):
        table_names = self.db.get_table_names()
        self.assertEqual(len(table_names), 1)
        self.assertEqual(table_names[0],
                         sql_model.CarbonIntensityRecord.__tablename__)

    def test_read(self):
        """Read back data to check."""
        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "high")
        results = sql_model.CarbonIntensityTable.read_all(self.engine,
                                                          statement)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].actual, 259)
        self.assertEqual(results[0].forecast, 254)
        self.assertEqual(results[0].rating, 'high')

    def test_call_multiple(self):
        """Add multiple entries, then read back to check."""
        lambda_processing.lambda_processing(self.test_event,
                                            self.engine)
        table_names = self.db.get_table_names()
        self.assertEqual(len(table_names), 1)
        statement = select(sql_model.CarbonIntensityTable).where(
                        sql_model.CarbonIntensityTable.rating == "high")
        results = sql_model.CarbonIntensityTable.read_all(self.engine,
                                                          statement)
        self.assertEqual(len(results), 2)

    def test_bad_event_data(self):
        """Not a valid SQS event object."""
        with self.assertRaises(pydantic.ValidationError):
            bad_event_data = {"Records": "no"}
            lambda_processing.lambda_processing(bad_event_data,
                                                self.engine)

    def tearDown(self) -> None:
        """Optionally pause the tests to allow database inspection."""
        if os.getenv('STEP_TESTS', None):
            print()
            print(f'Finished test: {unittest.TestCase.id(self)}')
            input("Press Enter to tear down...")
        self.db.tearDown()
        return super().tearDown()


class TestLambdaProcessingSQLite(TestLambdaProcessing):
    """This uses manual engine creation and SQLite."""

    def make_engine(self) -> Engine:
        return create_engine(f"sqlite:///{self.db.dbname}")

    def prepare_database(self) -> SQLiteHelper:
        return SQLiteHelper()


class TestCreateSQLEngineSQLite(TestLambdaProcessing):
    """This uses the engine creation function and SQLite."""

    def make_engine(self) -> Engine:
        db_user = None
        db_name = str(self.db.dbname)
        db_host = ''
        db_port = None
        db_password = None
        db_dialect_driver = "sqlite"
        return lambda_processing.create_sql_engine(db_name, db_user, db_host,
                                                   db_port, db_password,
                                                   db_dialect_driver)

    def prepare_database(self) -> SQLiteHelper:
        return SQLiteHelper()


class TestCreateSQLEnginePSQL(TestLambdaProcessing):
    """This uses the engine creation function and Postgresql."""

    def setUp(self) -> None:
        try:
            self.user = os.environ['TEST_DB_USER']
            self.dbname = os.environ['TEST_DB_NAME']
            self.host = os.getenv('TEST_DB_HOST', None)
            self.port = os.getenv('TEST_DB_PORT', None)
            self.password = os.getenv('TEST_DB_PASSWORD', None)
            self.dialect_driver = os.getenv('TEST_DB_DIALECT_DRIVER',
                                            'postgresql+psycopg2')
        except KeyError:
            print()
            print("TEST_DB_* parameter(s) not set: skipping test")
            self.skipTest("skip")
        super().setUp()

    def make_engine(self) -> Engine:
        return lambda_processing.create_sql_engine(self.dbname, self.user,
                                                   self.host, self.port,
                                                   self.password,
                                                   self.dialect_driver)

    def prepare_database(self) -> PSQLHelper:
        kw = {k: getattr(self, k) for k in
              ['dbname', 'user', 'host', 'port', 'password']}
        return PSQLHelper(**kw)


if __name__ == '__main__':
    unittest.main()
