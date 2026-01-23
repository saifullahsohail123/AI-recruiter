import sqlite3
from pathlib import Path
from typing import Dict, Any, List
import os
import json


class JobDatabase:
    def __init__(self):
        # Get the directory where database.py is located
        current_dir = Path(__file__).parent
        self.db_path = current_dir / "jobs.db"
        self.schema_path = current_dir / "schema.sql"
        self._init_db()

    def _init_db(self):
        # Initialize the database with schema
        if not self.schema_path.exsist():
            raise FileNotFoundError(f"Schema file not found at {self.schema_path}")
        
        with open(self.schema_path, "r") as f:
            schema = f.read()

        with sqlite3.connect(self.db_path) as conn:
            conn.executescript(schema)
            

