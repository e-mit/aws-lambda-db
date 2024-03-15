"""Classes to assist in creating temporary databases for tests."""

from pathlib import Path
import tempfile
import sqlite3
from typing import Any
from abc import ABC, abstractmethod
import os

import psycopg2
from psycopg2 import sql


class DBhelper(ABC):
    """Do simple CRUD operations on an undefined SQL database."""

    @abstractmethod
    def connect(self, **kwargs) -> Any:
        ...

    @property
    @abstractmethod
    def list_table_query(self) -> str:
        ...

    def __init__(self, dbname: str = '', **kwargs):
        """Connect to the database."""
        self.dbname = dbname
        kwargs['dbname'] = dbname
        self.conn = self.connect(**kwargs)

    def execute(self, query: str) -> list[Any]:
        """Execute a query and return data as a list."""
        cursor = self.conn.cursor()
        cursor.execute(query)
        values = cursor.fetchall()
        cursor.close()
        return values

    def get_table_length(self, table_name: str) -> int:
        data = self.execute(f"SELECT count(*) FROM {table_name};")
        return data[0][0]

    def get_table_names(self) -> list[str]:
        tables = self.execute(self.list_table_query)
        return [x[0] for x in tables]

    def tearDown(self) -> None:
        self.conn.close()

    @abstractmethod
    def set_environment_variables(self) -> None:
        ...


class SQLiteHelper(DBhelper):
    """Create a SQLite database for CRUD, then delete the whole database."""

    def connect(self, **kwargs) -> sqlite3.Connection:
        return sqlite3.connect(self.dbname)

    @property
    def list_table_query(self) -> str:
        return "SELECT name FROM sqlite_master WHERE type='table';"

    def __init__(self, dbname: str = '', **kwargs):
        """Create an empty database."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dbname = str(Path(self.temp_dir.name) / "temp.db")
        super().__init__(dbname=self.dbname)

    def tearDown(self) -> None:
        """Delete the database."""
        super().tearDown()
        self.temp_dir.cleanup()

    def set_environment_variables(self):
        os.environ['DB_USER'] = ''
        os.environ['DB_NAME'] = self.dbname
        os.environ['DB_PASSWORD'] = ''
        os.environ['DB_HOST'] = ''
        os.environ['DB_PORT'] = ''
        os.environ['DB_DIALECT_DRIVER'] = 'sqlite'


class PSQLHelper(DBhelper):
    """Connect to an existing postgres database, drop all its tables."""

    def connect(self, **kwargs):
        return psycopg2.connect(**kwargs)

    @property
    def list_table_query(self) -> str:
        return ("SELECT table_name FROM information_schema.tables "
                "where table_schema='public';")

    def drop_tables(self):
        table_names = self.get_table_names()
        for table_name in table_names:
            cur = self.conn.cursor()
            cur.execute(sql.SQL('DROP TABLE {table};').format(
                table=sql.Identifier(table_name)))
            self.conn.commit()
            cur.close()

    def __init__(self, dbname: str = '', **kwargs):
        """Connect to the database and delete all tables."""
        super().__init__(dbname, **kwargs)
        self.drop_tables()

    def tearDown(self) -> None:
        """Delete all tables but leave the database."""
        self.drop_tables()
        super().tearDown()

    def set_environment_variables(self) -> None:
        ...  # TODO
