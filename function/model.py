"""Pydantic model for data from https://api.carbonintensity.org.uk/intensity"""

from datetime import datetime
from typing import Literal, Annotated
from annotated_types import Len

from pydantic import BaseModel, Field


class CarbonIntensity(BaseModel):
    rating: Literal[
        'very low', 'low', 'moderate', 'high', 'very high'] = Field(
            validation_alias='index')
    forecast: int
    actual: int


class CarbonIntensityData(BaseModel):
    from_ts: datetime = Field(validation_alias='from')
    to_ts: datetime = Field(validation_alias='to')
    intensity: CarbonIntensity


class CarbonIntensityResponse(BaseModel):
    """The REST API produces a json string corresponding to this class."""
    data: Annotated[list[CarbonIntensityData], Len(min_length=1, max_length=1)]


def validate_json(api_response_txt: str) -> CarbonIntensityResponse:
    """Create a validated model object from a json string."""
    return CarbonIntensityResponse.model_validate_json(api_response_txt)


def validate_dict(api_response: dict) -> CarbonIntensityResponse:
    """Create a validated model object from a dictionary."""
    return CarbonIntensityResponse.model_validate(api_response)
