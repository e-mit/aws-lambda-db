import unittest
import os
import sys
import importlib
import json

sys.path.append("function")

os.environ['LOG_LEVEL'] = 'INFO'
sqlite_settings = {'DB_USER': 'theUser', 'DB_NAME': 'theName',
                   'DB_PASSWORD': '', 'DB_HOST': 'todo',
                   'DB_PORT': ''}
for k in sqlite_settings:
    os.environ[k] = sqlite_settings[k]

from function import lambda_function  # noqa


class TestFunction(unittest.TestCase):

    def test_function(self):
        event = {'desc': 'Test event'}
        context = {'requestid': '1234'}
        lambda_function.lambda_handler(event, context)
        self.assertEqual(0, 1)


if __name__ == '__main__':
    unittest.main()
