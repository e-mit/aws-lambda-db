import unittest
import sys
import json

from sqlmodel import select
import pydantic

sys.path.append("function")

from function import lambda_processing, sql_model  # noqa
from sqlite_helper import SQLiteHelper  # noqa

#database_settings = {'DB_USER': 'e', 'DB_NAME': 'test_lambda',
#                     'DB_PASSWORD': '', 'DB_HOST': 'localhost',
#                     'DB_PORT': ''}
#for k in database_settings:
#    os.environ[k] = database_settings[k]


class TestFunctionSQLite(unittest.TestCase):

    def setUp(self) -> None:
        with open('tests/test_sqs_event.json') as file:
            self.test_event = json.load(file)
        self.sqlite = SQLiteHelper()
        lambda_processing.lambda_processing(self.test_event,
                                            self.sqlite.engine)
        return super().setUp()

    def test_table_exists(self):
        table_names = self.sqlite.get_table_names()
        self.assertEqual(len(table_names), 1)
        self.assertEqual(table_names[0],
                         sql_model.CarbonIntensityRecord.__tablename__)

    def test_read(self):
        """Read back data to check."""
        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "high")
        results = sql_model.CarbonIntensityTable.read_all(self.sqlite.engine,
                                                          statement)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].actual, 259)
        self.assertEqual(results[0].forecast, 254)
        self.assertEqual(results[0].rating, 'high')

    def test_call_multiple(self):
        """Add multiple entries, then read back to check."""
        lambda_processing.lambda_processing(self.test_event,
                                            self.sqlite.engine)
        table_names = self.sqlite.get_table_names()
        self.assertEqual(len(table_names), 1)
        statement = select(sql_model.CarbonIntensityTable).where(
                        sql_model.CarbonIntensityTable.rating == "high")
        results = sql_model.CarbonIntensityTable.read_all(self.sqlite.engine,
                                                          statement)
        self.assertEqual(len(results), 2)

    def test_bad_event_data(self):
        """Not a valid SQS event object."""
        with self.assertRaises(pydantic.ValidationError):
            bad_event_data = {"Records": "no"}
            lambda_processing.lambda_processing(bad_event_data,
                                                self.sqlite.engine)

    def tearDown(self) -> None:
        self.sqlite.tearDown()
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
