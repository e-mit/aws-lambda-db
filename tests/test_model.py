import unittest
import sys
import json

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


if __name__ == '__main__':
    unittest.main()
