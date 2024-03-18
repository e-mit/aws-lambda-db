"""SQL database model for https://api.carbonintensity.org.uk/intensity"""

from typing import Annotated
from typing_extensions import Self
from datetime import datetime

from pydantic import AfterValidator

import source_model
import sqlmodel
import sql_model_base


def validate_rating(rating: str) -> str:
    """Allow only fixed set of values."""
    assert rating in ['very low', 'low', 'moderate', 'high', 'very high']
    return rating


class CarbonIntensityRecord(
        sql_model_base.DataModel[source_model.CarbonIntensityData]):
    """This is a pydantic/sqlmodel class for database data validation."""
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


class CarbonIntensityTable(
        CarbonIntensityRecord,
        sql_model_base.DataModelTable[
            CarbonIntensityRecord, source_model.CarbonIntensityData],
        table=True):
    """This is used as the database interface (does not perform validation)."""
    id: int | None = sqlmodel.Field(default=None, primary_key=True)
