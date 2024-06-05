import unittest
import sys
import json

import pydantic

sys.path.append("function")

from function import source_model  # noqa


class TestModel(unittest.TestCase):

    def test_model_json(self):
        with open('tests/test_api_response.txt', 'r') as file:
            payload_txt = file.read()
        data_object = source_model.validate_json(payload_txt)
        self.assertEqual(len(data_object.data), 1)
        self.assertEqual(data_object.data[0].intensity.actual, 242)
        self.assertEqual(data_object.data[0].intensity.rating, 'high')

    def test_model_dict(self):
        with open('tests/test_api_response.txt', 'r') as file:
            payload_txt = file.read()
        data_object = source_model.validate_dict(json.loads(payload_txt))
        self.assertEqual(len(data_object.data), 1)
        self.assertEqual(data_object.data[0].intensity.actual, 242)
        self.assertEqual(data_object.data[0].intensity.rating, 'high')


class TestNulls(unittest.TestCase):

    def test_actual_null(self):
        with open('tests/test_api_actual_null.txt', 'r') as file:
            payload_txt = file.read()
        data_object = source_model.validate_json(payload_txt)
        self.assertEqual(len(data_object.data), 1)
        self.assertEqual(data_object.data[0].intensity.actual, 31)
        self.assertEqual(data_object.data[0].intensity.forecast, 31)

    def test_forecast_null(self):
        with open('tests/test_api_forecast_null.txt', 'r') as file:
            payload_txt = file.read()
        data_object = source_model.validate_json(payload_txt)
        self.assertEqual(len(data_object.data), 1)
        self.assertEqual(data_object.data[0].intensity.actual, 31)
        self.assertEqual(data_object.data[0].intensity.forecast, 31)

    def test_both_null(self):
        with open('tests/test_api_both_null.txt', 'r') as file:
            payload_txt = file.read()
        with self.assertRaises(pydantic.ValidationError):
            source_model.validate_json(payload_txt)


if __name__ == '__main__':
    unittest.main()
