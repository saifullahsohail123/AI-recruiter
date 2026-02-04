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

    def add_job(self, job_data: Dict[str, Any]) -> int:
        """ Add a new job to the database and return its ID. """
            

        query = """
                INSERT INTO jobs (title,company,location, type, experience_level, 
                salary_range, description, requirements, benefits) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                job_data.get("title"),
                job_data.get("company"),
                job_data.get("location"),
                job_data.get("type"),
                job_data.get("experience_level"),
                json.dumps(job_data.get("salary_range")),
                job_data.get("description"),
                json.dumps(job_data.get("requirements")),
                json.dumps(job_data.get("benefits"))
            ))
            conn.commit()
            return cursor.lastrowid
        
    def get_all_jobs(self) -> List[Dict[str, Any]]:
        """ Retrieve all jobs from the database. """
        query = "SELECT * FROM jobs"
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            rows = cursor.fetchall()
            jobs = []
            for row in rows:
                job = {
                    "id": row[0],
                    "title": row[1],
                    "company": row[2],
                    "location": row[3],
                    "type": row[4],
                    "experience_level": row[5],
                    "salary_range": json.loads(row[6]),
                    "description": row[7],
                    "requirements": json.loads(row[8]),
                    "benefits": json.loads(row[9])
                }
                jobs.append(job)
            return jobs
        

        def search_jobs(self, skills: List[str], experience_level: str) -> List[Dict[str, Any]]:
            """ Search jobs based on skills and experience level. """
            query  = """
                    SELECT * FROM jobs WHERE experience_level = ? 
                    AND
                     (
                     """
            query_conditions = []
            params = [experience_level]

            # Create LIKE conditions for each skill
            for skill in skills:
                query_conditions.append("requirements LIKE ?")
                params.append(f"%{skill}%")

            query += "OR ".join(query_conditions) + ")"


            try:
                with sqlite3.connect(self.db_path) as conn:
                    cursor = conn.cursor()
                    cursor.execute(query, params)
                    rows = cursor.fetchall()
                    jobs = []
                    for row in rows:
                        job = {
                            "id": row[0],
                            "title": row[1],
                            "company": row[2],
                            "location": row[3],
                            "type": row[4],
                            "experience_level": row[5],
                            "salary_range": json.loads(row[6]),
                            "description": row[7],
                            "requirements": json.loads(row[8]),
                            "benefits": json.loads(row[9])
                        }
                        jobs.append(job)
                    return jobs
            except Exception as e:
                print(f"Error searching jobs: {e}")
                return []
            
