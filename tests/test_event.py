import unittest
import sys
import json

sys.path.append("function")

from function import event_data  # noqa


class TestEvent(unittest.TestCase):

    def setUp(self) -> None:
        with open('tests/test_sqs_event.json') as file:
            self.event = json.load(file)
        self.exp_payload = (
            {"data": [{"from": "2024-03-11T18:30Z",
                       "to": "2024-03-11T19:00Z",
                       "intensity": {"forecast": 254, "actual": 259,
                                     "index": "high"}}]})
        return super().setUp()

    def test_event_model(self):
        event = event_data.SQSEvent(**self.event)
        self.assertEqual(len(event.Records), 1)
        self.assertEqual(event.Records[0].awsRegion, 'eu-west-2')
        self.assertEqual(event.Records[0].body.version, '1.0')
        self.assertEqual(event.Records[0].body.responsePayload,
                         self.exp_payload)

    def test_extract(self):
        payloads = []
        for payload_txt in event_data.extract(self.event):
            payloads.append(payload_txt)
        self.assertEqual(len(payloads), 1)
        self.assertEqual(payloads[0], self.exp_payload)


if __name__ == '__main__':
    unittest.main()
