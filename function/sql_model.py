"""SQL database model for https://api.carbonintensity.org.uk/intensity data."""

from typing import Annotated
from datetime import datetime

from typing_extensions import Self
from pydantic import AfterValidator

import source_model
import sqlmodel
import sql_model_base


def validate_rating(rating: str) -> str:
    """Allow only fixed set of values."""
    if rating not in ['very low', 'low', 'moderate', 'high', 'very high']:
        raise AssertionError("Carbon intensity rating: invalid value.")
    return rating


# pylint: disable=R0903
class CarbonIntensityRecord(
        sql_model_base.DataModel[source_model.CarbonIntensityData]):
    """A pydantic/sqlmodel class for database data validation."""

    rating: Annotated[str, AfterValidator(validate_rating)]
    forecast: int
    actual: int
    time: datetime

    @classmethod
    def from_source_model(cls,
                          source_data: source_model.CarbonIntensityData
                          ) -> Self:
        """Convert data from the source API into the desired db format."""
        half_dt = (source_data.to_ts - source_data.from_ts)/2
        midpoint = source_data.from_ts + half_dt
        return cls(forecast=source_data.intensity.forecast,
                   actual=source_data.intensity.actual,
                   rating=source_data.intensity.rating,
                   time=midpoint)
# pylint: enable=R0903


class CarbonIntensityTable(
        CarbonIntensityRecord,
        sql_model_base.DataModelTable[
            CarbonIntensityRecord, source_model.CarbonIntensityData],
        table=True):
    """Provides the database interface (does not perform validation)."""

    id: int | None = sqlmodel.Field(default=None, primary_key=True)
