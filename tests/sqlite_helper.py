from pathlib import Path
import tempfile
import sqlite3
from typing import Any

from sqlmodel import SQLModel, create_engine


class SQLiteHelper:

    def __init__(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_db_file = Path(self.temp_dir.name) / "temp.db"
        self.engine = create_engine(f"sqlite:///{self.temp_db_file}")
        SQLModel.metadata.create_all(self.engine)
        self.conn = sqlite3.connect(self.temp_db_file)

    def execute(self, query: str) -> list[Any]:
        cursor = self.conn.cursor()
        cursor.execute(query)
        values = cursor.fetchall()
        cursor.close()
        return values

    def get_table_length(self, table_name: str) -> int:
        data = self.execute(f"SELECT count(*) FROM {table_name};")
        return data[0][0]

    def get_table_names(self) -> list[str]:
        tables = self.execute(
            "SELECT name FROM sqlite_master WHERE type='table';")
        return [x[0] for x in tables]

    def tearDown(self) -> None:
        self.conn.close()
        self.temp_dir.cleanup()
