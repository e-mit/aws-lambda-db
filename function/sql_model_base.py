"""Generic SQL database model for API data"""

from typing import Optional, Annotated, Literal
from typing import overload, Any, Generic, TypeVar
from typing_extensions import Self
from datetime import datetime
from abc import abstractmethod, ABC

from pydantic import AfterValidator, BaseModel
from sqlmodel import Field, SQLModel, Session
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import Engine


SourceModel = TypeVar("SourceModel")


class DataModel(SQLModel, ABC, Generic[SourceModel]):
    """This is a pydantic class for data validation."""

    @classmethod
    @abstractmethod
    def from_source_model(cls,
                          source_data: SourceModel
                          ) -> Self:
        """Convert data obtained from the API into the desired db format."""
        ...


# class DataModelTable(DataModel, table=True):
#     """This is used as the database interface (does not perform validation)."""
#     id: Optional[int] = Field(default=None, primary_key=True)

#     def __new__(cls, ModelClass):
#         cls.ModelClass = ModelClass
#         cls.__tablename__ = ModelClass.__tablename__
#         return super().__new__(cls)

#     @classmethod
#     def _create_table_item_from_model(cls,
#                                       entry: cls.ModelClass) -> Self:
#         return cls(**{k: getattr(entry, k) for k in entry.model_fields})

#     @classmethod
#     def _create_model_from_table_item(cls,
#                                       item: Self) -> CarbonIntensityRecord:
#         return cls.ModelClass(
#             **{k: getattr(item, k) for k in item.model_fields})

#     @classmethod
#     def _add(cls, engine: Engine, item: Self) -> None:
#         with Session(engine) as session:
#             session.add(item)
#             session.commit()

#     @classmethod
#     def add_from_db_model(cls, engine: Engine,
#                           entry: CarbonIntensityRecord) -> None:
#         """Use an object that was validated to match the database schema."""
#         item = cls._create_table_item_from_model(entry)
#         cls._add(engine, item)

#     @classmethod
#     def add_from_source_model(cls, engine: Engine,
#                               source_data: BaseModel
#                               ) -> None:
#         """Use an object that was validated to match the source API."""
#         item = cls.ModelClass.from_source_model(source_data)
#         cls.add_from_db_model(engine, item)

#     @overload
#     @classmethod
#     def _read(cls, engine: Engine, method: Literal['all'],
#               statement: SelectOfScalar[Self]) -> list[Self]: ...

#     @overload
#     @classmethod
#     def _read(cls, engine: Engine, method: Literal['first'],
#               statement: SelectOfScalar[Self]) -> Self: ...

#     @classmethod
#     def _read(cls, engine: Engine, method: Literal['all', 'first'],
#               statement: SelectOfScalar[Self]) -> list[Self] | Self:
#         with Session(engine) as session:
#             return getattr(session.exec(statement), method)()

#     @classmethod
#     def read_all(cls, engine: Engine,
#                  statement: SelectOfScalar[Self]
#                  ) -> list[CarbonIntensityRecord]:
#         return [cls._create_model_from_table_item(x) for x in
#                 cls._read(engine, 'all', statement)]

#     @classmethod
#     def read_first(cls, engine: Engine,
#                    statement: SelectOfScalar[Self]) -> CarbonIntensityRecord:
#         return cls._create_model_from_table_item(
#                         cls._read(engine, 'first', statement))
