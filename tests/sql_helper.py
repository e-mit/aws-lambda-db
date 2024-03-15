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
    dbname: str
    user: str | None
    host: str | None
    port: str | None
    password: str | None
    dialect_driver: str

    @abstractmethod
    def connect(self) -> Any:
        ...

    @property
    @abstractmethod
    def list_table_query(self) -> str:
        ...

    @abstractmethod
    def set_environment_variables(self) -> None:
        ...

    def __init__(self):
        """Connect to the database."""
        self.conn = self.connect()

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


class SQLiteHelper(DBhelper):
    """Create a SQLite database for CRUD, then delete the whole database."""

    def connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.dbname)

    @property
    def list_table_query(self) -> str:
        return "SELECT name FROM sqlite_master WHERE type='table';"

    def __init__(self):
        """Create an empty database."""
        self.dialect_driver = 'sqlite'
        self.temp_dir = tempfile.TemporaryDirectory()
        self.dbname = str(Path(self.temp_dir.name) / "temp.db")
        super().__init__()

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
        os.environ['DB_DIALECT_DRIVER'] = self.dialect_driver


class PSQLHelper(DBhelper):
    """Connect to an existing postgres database, drop all its tables."""

    POSTGRES_DIALECT = 'postgresql+psycopg2'

    def connect(self):
        kw = {k: getattr(self, k) for k in
              ['dbname', 'user', 'host', 'port', 'password']}
        return psycopg2.connect(**kw)

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

    def __init__(self):
        """Connect to the database and delete all tables."""
        self.get_test_environment_variables()
        super().__init__()
        self.drop_tables()

    def tearDown(self) -> None:
        """Delete all tables but leave the database."""
        self.drop_tables()
        super().tearDown()

    def get_test_environment_variables(self) -> None:
        """Raises KeyError if var(s) not set."""
        self.user = os.environ['TEST_DB_USER']
        self.dbname = os.environ['TEST_DB_NAME']
        self.host = os.getenv('TEST_DB_HOST', None)
        self.port = os.getenv('TEST_DB_PORT', None)
        self.password = os.getenv('TEST_DB_PASSWORD', None)
        self.dialect_driver = os.getenv('TEST_DB_DIALECT_DRIVER',
                                        self.POSTGRES_DIALECT)
        if self.dialect_driver != self.POSTGRES_DIALECT:
            raise ValueError("Unexpected database dialect/driver.")

    def set_environment_variables(self):
        os.environ['DB_USER'] = self.user or ''
        os.environ['DB_NAME'] = self.dbname
        os.environ['DB_PASSWORD'] = self.password or ''
        os.environ['DB_HOST'] = self.host or ''
        os.environ['DB_PORT'] = self.port or ''
        os.environ['DB_DIALECT_DRIVER'] = self.POSTGRES_DIALECT
