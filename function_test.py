import unittest
import logging
import sys

sys.path.append("function")

from function import lambda_function  # noqa

logger = logging.getLogger()
handler = lambda_function.lambda_handler


class TestFunction(unittest.TestCase):

    def test_function(self):
        event = "{'desc': 'Test event'}"
        logger.info(f'Test event: {event}')
        context = {'requestid': '1234'}
        result = handler(event, context)
        print(str(result))
        self.assertIn("data", result)
        self.assertEqual(len(result['data']), 1)


if __name__ == '__main__':
    unittest.main()
