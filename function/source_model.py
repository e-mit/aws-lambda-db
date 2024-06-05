"""Pydantic model for https://api.carbonintensity.org.uk/intensity data."""

from datetime import datetime
from typing import Literal, Annotated
from typing_extensions import Self
from annotated_types import Len

from pydantic import BaseModel, Field, model_validator


class CarbonIntensity(BaseModel):
    """Sub-object of data contained in the REST API response."""

    rating: Literal[
        'very low', 'low', 'moderate', 'high', 'very high'] = Field(
            validation_alias='index')
    forecast: int | None
    actual: int | None

    @model_validator(mode='after')
    def remove_nulls(self) -> Self:
        """Try to remove nulls from the API data where possible."""
        if self.actual is None and self.forecast is None:
            raise ValueError('Both intensities are null.')
        if self.actual is None:
            self.actual = self.forecast
        elif self.forecast is None:
            self.forecast = self.actual
        return self


class CarbonIntensityData(BaseModel):
    """Data object contained in the REST API response."""

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
