import unittest
import os
import sys
import json
import importlib
from typing import Any

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


class TestFunctionSQLite(unittest.TestCase):

    def setUp(self) -> None:
        with open('tests/test_sqs_event.json') as file:
            self.test_event: dict[str, Any] = json.load(file)
        self.db = SQLiteHelper()
        self.db.set_environment_variables()
        # reimport the module to apply new environment variables
        importlib.reload(lambda_function)
        return super().setUp()

    def test_function(self):
        test_context = {'requestid': '1234'}
        lambda_function.lambda_handler(self.test_event, test_context)
        # now check the database:

    def tearDown(self) -> None:
        """Optionally pause the tests to allow database inspection."""
        if os.getenv('STEP_TESTS', None):
            print()
            print(f'Finished test: {unittest.TestCase.id(self)}')
            input("Press Enter to tear down...")
        self.db.tearDown()
        return super().tearDown()


if __name__ == '__main__':
    unittest.main()
