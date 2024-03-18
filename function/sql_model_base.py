"""Generic SQL database model for API data"""

from typing import Literal, overload, Generic, TypeVar
from typing_extensions import Self
from abc import abstractmethod, ABC

from sqlmodel import SQLModel, Session
from sqlmodel.sql.expression import SelectOfScalar
from sqlalchemy import Engine
import pydantic

SourceModelClass = TypeVar("SourceModelClass", bound=pydantic.BaseModel)


class DataModel(SQLModel, ABC, Generic[SourceModelClass]):
    """This is a pydantic class for data validation."""

    @classmethod
    @abstractmethod
    def from_source_model(cls,
                          source_data: SourceModelClass
                          ) -> Self:
        """Convert data obtained from the API into the desired db format."""
        ...


DataModelClass = TypeVar("DataModelClass", bound=DataModel)


class DataModelTable(Generic[DataModelClass, SourceModelClass]):
    """This is used as the database interface (does not perform validation)."""

    def __init_subclass__(cls):
        cls.__tablename__: str = cls.__bases__[0].__tablename__  # type: ignore

    @classmethod
    def _create_table_item_from_model(cls,
                                      entry: DataModelClass) -> Self:
        return cls(**{k: getattr(entry, k) for k in entry.model_fields})

    @classmethod
    def _create_model_from_table_item(cls,
                                      item: Self) -> DataModelClass:
        return cls.__bases__[0](
            **{k: getattr(item, k) for k in item.model_fields})

    @classmethod
    def _add(cls, engine: Engine, item: Self) -> None:
        with Session(engine) as session:
            session.add(item)
            session.commit()

    @classmethod
    def add_from_db_model(cls, engine: Engine,
                          entry: DataModelClass) -> None:
        """Use an object that was validated to match the database schema."""
        item = cls._create_table_item_from_model(entry)
        cls._add(engine, item)

    @classmethod
    def add_from_source_model(cls, engine: Engine,
                              source_data: SourceModelClass
                              ) -> None:
        """Use an object that was validated to match the source API."""
        item = cls.__bases__[0].from_source_model(source_data)
        cls.add_from_db_model(engine, item)

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
                 statement: SelectOfScalar[Self]
                 ) -> list[DataModelClass]:
        return [cls._create_model_from_table_item(x) for x in
                cls._read(engine, 'all', statement)]

    @classmethod
    def read_first(cls, engine: Engine,
                   statement: SelectOfScalar[Self]) -> DataModelClass:
        return cls._create_model_from_table_item(
                        cls._read(engine, 'first', statement))
