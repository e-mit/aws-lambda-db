from typing import Optional, Annotated, Literal, overload
from typing_extensions import Self
from datetime import datetime

from pydantic import AfterValidator
from sqlmodel import Field, SQLModel, Session
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import Engine


def validate_rating(rating: str) -> str:
    """Allow only fixed set of values."""
    assert rating in ['very low', 'low', 'moderate', 'high', 'very high']
    return rating


class CarbonIntensity(SQLModel):
    rating: Annotated[str, AfterValidator(validate_rating)]
    forecast: int
    actual: int
    time: datetime


class CarbonIntensityTable(CarbonIntensity, table=True):
    __tablename__: str = CarbonIntensity.__tablename__  # type: ignore
    id: Optional[int] = Field(default=None, primary_key=True)

    @classmethod
    def _create_table_item_from_model(cls, entry: CarbonIntensity) -> Self:
        return cls(**{k: getattr(entry, k) for k in entry.model_fields})

    @classmethod
    def _create_model_from_table_item(cls, item: Self) -> CarbonIntensity:
        return CarbonIntensity(
            **{k: getattr(item, k) for k in item.model_fields})

    @classmethod
    def add_from_db_model(cls, engine: Engine, entry: CarbonIntensity) -> None:
        """Use an object that is validated to match the database schema."""
        item = cls._create_table_item_from_model(entry)
        with Session(engine) as session:
            session.add(item)
            session.commit()

    @overload
    @classmethod
    def _read(cls, engine: Engine, method: Literal['all'],
              statement: SelectOfScalar[Self]) -> list[Self]: ...

    @overload
    @classmethod
    def _read(cls, engine: Engine, method: Literal['first'],
              statement: SelectOfScalar[Self]) -> Self: ...

    @classmethod
    def _read(cls, engine: Engine, method: Literal['all', 'first'],
              statement: SelectOfScalar[Self]) -> list[Self] | Self:
        with Session(engine) as session:
            return getattr(session.exec(statement), method)()

    @classmethod
    def read_all(cls, engine: Engine,
                 statement: SelectOfScalar[Self]) -> list[CarbonIntensity]:
        return [cls._create_model_from_table_item(x) for x in
                cls._read(engine, 'all', statement)]

    @classmethod
    def read_first(cls, engine: Engine,
                   statement: SelectOfScalar[Self]) -> CarbonIntensity:
        return cls._create_model_from_table_item(
                        cls._read(engine, 'first', statement))
