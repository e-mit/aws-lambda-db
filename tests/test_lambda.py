import unittest
import os
import sys
import json
import importlib
from typing import Any

from sqlmodel import select
import pydantic


# Set dummy variables:
os.environ['LOG_LEVEL'] = 'CRITICAL'
os.environ['DB_USER'] = ''
os.environ['DB_NAME'] = ''
os.environ['DB_PASSWORD'] = ''
os.environ['DB_HOST'] = ''
os.environ['DB_PORT'] = ''
os.environ['DB_DIALECT_DRIVER'] = 'sqlite'


sys.path.append("function")
from function import lambda_function  # noqa
from sql_helper import SQLiteHelper, PSQLHelper, DBhelper  # noqa
from function import sql_model  # noqa


class TestFunctionSQL(unittest.TestCase):

    def get_db(self) -> DBhelper:
        print()
        print(f"Skipping test of abstract class {type(self).__name__}.")
        self.skipTest("ABC")

    def setUp(self) -> None:
        with open('tests/test_sqs_event.json') as file:
            self.test_event: dict[str, Any] = json.load(file)
        self.db = self.get_db()
        self.db.set_environment_variables()
        # reimport the module to apply new environment variables:
        importlib.reload(lambda_function)
        # call the function:
        self.test_context = {'requestid': '1234'}
        lambda_function.lambda_handler(self.test_event, self.test_context)
        return super().setUp()

    def tearDown(self) -> None:
        """Optionally pause the tests to allow database inspection."""
        if os.getenv('STEP_TESTS', None):
            print()
            print(f'Finished test: {unittest.TestCase.id(self)}')
            input("Press Enter to tear down...")
        self.db.tearDown()
        return super().tearDown()

    def test_table_exists(self):
        """There should be exactly one table in the database."""
        table_names = self.db.get_table_names()
        self.assertEqual(len(table_names), 1)
        self.assertEqual(table_names[0],
                         sql_model.CarbonIntensityRecord.__tablename__)

    def test_read(self):
        """There should be one record in the table: read back and check."""
        statement = select(sql_model.CarbonIntensityTable)
        results = sql_model.CarbonIntensityTable.read_all(
            lambda_function.engine, statement)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].actual, 259)
        self.assertEqual(results[0].forecast, 254)
        self.assertEqual(results[0].rating, 'high')

    def test_call_multiple(self):
        """Add two entries, then read back to check."""
        lambda_function.lambda_handler(self.test_event, self.test_context)
        table_names = self.db.get_table_names()
        self.assertEqual(len(table_names), 1)
        statement = select(sql_model.CarbonIntensityTable)
        results = sql_model.CarbonIntensityTable.read_all(
            lambda_function.engine, statement)
        self.assertEqual(len(results), 2)

    def test_bad_event_data(self):
        """Not a valid SQS event object."""
        with self.assertRaises(pydantic.ValidationError):
            bad_event_data = {"Records": "no"}
            lambda_function.lambda_handler(bad_event_data, self.test_context)


class TestFunctionSQLite(TestFunctionSQL):

    def get_db(self) -> DBhelper:
        return SQLiteHelper()


class TestFunctionPSQL(TestFunctionSQL):

    def get_db(self) -> DBhelper:
        """This causes the test to skip if the DB params are not provided."""
        try:
            db = PSQLHelper()
        except KeyError:
            print()
            print(f"{type(self).__name__}: "
                  "TEST_DB_* parameter(s) not set: skipping test")
            self.skipTest("skip")
        return db


if __name__ == '__main__':
    unittest.main()
