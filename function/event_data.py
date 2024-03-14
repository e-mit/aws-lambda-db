"""Pydantic model for validating AWS SQS event data input to Lambda.

This allows easy extraction of the 'responsePayload' field from the
event data, which is the (json) data originally enqueued in the SQS.
"""

from typing import Any, Iterator
from datetime import datetime
from typing import Literal, Annotated
from annotated_types import Len

from pydantic import BaseModel, BeforeValidator


class SQSRecordBody(BaseModel):
    version: str
    timestamp: datetime
    requestContext: dict
    requestPayload: dict
    responseContext: dict
    responsePayload: dict


class SQSRecord(BaseModel):
    messageId: str
    receiptHandle: str
    body: Annotated[SQSRecordBody,
                    BeforeValidator(SQSRecordBody.model_validate_json)]
    attributes: dict[str, str]
    messageAttributes: dict
    md5OfBody: str
    eventSource: Literal['aws:sqs']
    eventSourceARN: str
    awsRegion: str


class SQSEvent(BaseModel):
    Records: Annotated[list[SQSRecord], Len(min_length=1)]


def extract(event: dict[str, Any]) -> Iterator[dict]:
    """Obtain the dict that was originally enqueued in the SQS.

    Iterate over all messages in the event.
    """
    validated_event = SQSEvent(**event)
    for record in validated_event.Records:
        yield record.body.responsePayload
