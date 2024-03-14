"""Unit tests for file sql_model.py

Set environment variable STEP_TESTS to any value to step through SQL tests.
"""
import unittest
import sys
from datetime import datetime
from pathlib import Path
import tempfile
import sqlite3
from typing import Any
import os

from sqlmodel import SQLModel, create_engine, select
import pydantic

sys.path.append("function")

from function import sql_model, model  # noqa

TEST_ARGS = dict(rating="high", forecast=10,
                 actual=400, time=datetime.now())


class TestCarbonIntensity(unittest.TestCase):

    def setUp(self) -> None:
        return super().setUp()

    def test_sql_model(self):
        carb = sql_model.CarbonIntensity(**TEST_ARGS)  # type: ignore
        for i, tup in enumerate(carb):
            with self.subTest(i=i):
                self.assertEqual(tup[1], TEST_ARGS[tup[0]])

    def test_invalid_rating(self):
        with self.assertRaises(pydantic.ValidationError):
            sql_model.CarbonIntensity(rating="wrong", forecast=10,
                                      actual=400, time=datetime.now())

    def test_invalid_forecast(self):
        with self.assertRaises(pydantic.ValidationError):
            sql_model.CarbonIntensity(rating="low",
                                      forecast="wrong",  # type: ignore
                                      actual=400, time=datetime.now())

    def test_invalid_date(self):
        with self.assertRaises(pydantic.ValidationError):
            sql_model.CarbonIntensity(rating="low", forecast=10,
                                      actual=400, time="wrong")  # type: ignore

    def test_coercion(self):
        carb = sql_model.CarbonIntensity(
                    rating="low",
                    forecast=float(10.0),  # type: ignore
                    actual="4",  # type: ignore
                    time="2024-01-02 12:56")  # type: ignore
        self.assertIsInstance(carb, sql_model.CarbonIntensity)
        self.assertEqual(carb.actual, 4)
        self.assertIsInstance(carb.actual, int)
        self.assertEqual(carb.forecast, 10)
        self.assertIsInstance(carb.forecast, int)

    def test_from_source_model(self):
        with open('tests/test_api_response.txt', 'r') as file:
            payload_txt = file.read()
        source_data = model.validate_json(payload_txt).data[0]
        db_obj = sql_model.CarbonIntensity.from_source_model(source_data)
        self.assertEqual(db_obj.actual, 242)
        self.assertEqual(db_obj.forecast, 247)
        self.assertEqual(db_obj.rating, 'high')
        expected_time = datetime.fromisoformat("2024-03-11T15:45:00+00:00")
        self.assertEqual(db_obj.time, expected_time)


class TestCarbonIntensityTable(unittest.TestCase):

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_db_file = Path(self.temp_dir.name) / "temp.db"
        self.engine = create_engine(f"sqlite:///{self.temp_db_file}")
        SQLModel.metadata.create_all(self.engine)
        self.conn = sqlite3.connect(self.temp_db_file)

    def execute_SQLite(self, query: str) -> list[Any]:
        cursor = self.conn.cursor()
        cursor.execute(query)
        values = cursor.fetchall()
        cursor.close()
        return values

    def get_table_length(self, table_name: str) -> int:
        data = self.execute_SQLite(f"SELECT count(*) FROM {table_name};")
        return data[0][0]

    def test_table_exists(self):
        tables = self.execute_SQLite(
            "SELECT name FROM sqlite_master WHERE type='table';")
        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0][0], sql_model.CarbonIntensity.__tablename__)

    def test_create_table_item(self):
        carb = sql_model.CarbonIntensity(**TEST_ARGS)  # type: ignore
        item = sql_model.CarbonIntensityTable._create_table_item_from_model(
                                                                        carb)
        self.assertIsInstance(item, sql_model.CarbonIntensityTable)
        for i, tup in enumerate(carb):
            with self.subTest(i=i):
                self.assertEqual(tup[1], TEST_ARGS[tup[0]])

    def test_add_from_db_model(self):
        carb = sql_model.CarbonIntensity(**TEST_ARGS)  # type: ignore
        sql_model.CarbonIntensityTable.add_from_db_model(self.engine, carb)

        self.assertEqual(self.get_table_length(
            sql_model.CarbonIntensity.__tablename__), 1)  # type: ignore

        for k in TEST_ARGS:
            data = self.execute_SQLite(
                f"SELECT {k} FROM {sql_model.CarbonIntensity.__tablename__};")
            if k != 'time':
                with self.subTest(k=k):
                    self.assertEqual(data[0][0], TEST_ARGS[k])
            else:
                # Just compare the date and time up to the integer second
                with self.subTest(k=k):
                    self.assertEqual(data[0][0][0:19], str(TEST_ARGS[k])[0:19])

    def test_read_all(self):
        """Add multiple entries, then read back to check."""
        c1 = sql_model.CarbonIntensity(rating='very high', forecast=0,
                                       actual=999, time=datetime.now())
        sql_model.CarbonIntensityTable.add_from_db_model(self.engine, c1)
        c2 = sql_model.CarbonIntensity(rating='low', forecast=-10, actual=2,
                                       time=datetime.now())
        sql_model.CarbonIntensityTable.add_from_db_model(self.engine, c2)

        self.assertEqual(self.get_table_length(
            sql_model.CarbonIntensity.__tablename__), 2)  # type: ignore

        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "low")
        results = sql_model.CarbonIntensityTable.read_all(self.engine,
                                                          statement)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], c2)

        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "very high")
        results = sql_model.CarbonIntensityTable.read_all(self.engine,
                                                          statement)
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0], c1)

    def test_read_first(self):
        """Add multiple entries, then read back to check."""
        c1 = sql_model.CarbonIntensity(rating='very high', forecast=0,
                                       actual=999, time=datetime.now())
        sql_model.CarbonIntensityTable.add_from_db_model(self.engine, c1)
        c2 = sql_model.CarbonIntensity(rating='low', forecast=-10, actual=2,
                                       time=datetime.now())
        sql_model.CarbonIntensityTable.add_from_db_model(self.engine, c2)

        self.assertEqual(self.get_table_length(
            sql_model.CarbonIntensity.__tablename__), 2)  # type: ignore

        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "low")
        results = sql_model.CarbonIntensityTable.read_first(self.engine,
                                                            statement)
        self.assertEqual(results, c2)

        statement = select(sql_model.CarbonIntensityTable).where(
                sql_model.CarbonIntensityTable.rating == "very high")
        results = sql_model.CarbonIntensityTable.read_first(self.engine,
                                                            statement)
        self.assertEqual(results, c1)

    def tearDown(self) -> None:
        if os.getenv('STEP_TESTS', None):
            print('\nFinished test: ', unittest.TestCase.id(self))
            input("Press Enter to tear down...")
        self.conn.close()
        self.temp_dir.cleanup()
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
