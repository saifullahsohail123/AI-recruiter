from .base_agent import BaseAgent
from typing import Dict, Any
import json
import re # for regex operations

from db.database import JobDatabase  # Assume JobDatabase is defined elsewhere
import sqlite3


class MatcherAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="MatcherAgent",
            instructions=("""Match candidate profiles with job positions.
            Consider: skills match, experience level, location preferences.
            Provide detailed reasoning and compatibility scores.
            Return matches in JSON format with title, match_score, and location fields.""")
        )

        self.db = JobDatabase()  # Assume JobDatabase is defined elsewhere


    async def run(self, messages: list) -> Dict[str, Any]:
        """Match candidate with available positions"""
        print("🎯 Matcher: Finding suitable job matches")

        try:
            # Convert single quotes to double quotes to make it valid JSON
            content = messages[-1].get("content", "{}").replace("'", '"')
            analysis_results = json.loads(content)
        except json.JSONDecodeError as e:
            print(f"Error parsing analysis results: {e}")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0,
            }
        
        # Extract skills and experience level from analysis
        skills_analysis = analysis_results.get("skills_analysis", {})
        if not skills_analysis:
            print("No skills analysis found.")
            return {
                "matched_jobs": [],
                "match_timestamp": "2024-03-14",
                "number_of_matches": 0,
            }
        
        # Extract technical skills and experience level directly
        skills = skills_analysis.get("technical_skills", [])
        experience_level_raw = skills_analysis.get("experience_level", "Mid-level")

        # Normalize experience level to match DB values
        el = (experience_level_raw or "").lower()
        if "senior" in el:
            experience_level = "Senior"
        elif "mid" in el:
            experience_level = "Mid-level"
        elif "entry" in el:
            experience_level = "Entry-level"
        elif "junior" in el:
            experience_level = "Junior"
        else:
            # fall back to Mid-level if unknown
            print(f"Invalid experience level found ('{experience_level_raw}'), defaulting to 'Mid-level'.")
            experience_level = "Mid-level"

        if not isinstance(skills, list) or not skills:
            print("No valid skills found, defaulting to an empty list.")
            skills = []

        print(f" ==>>> Skills: {skills}, Experience Level: {experience_level}")
        # Search jobs database
        matching_jobs = self.search_jobs(skills, experience_level)

        # Calculate match scores using match_pct returned by search_jobs
        scored_jobs = []
        for job in matching_jobs:
            match_score = int(job.get("match_pct", 0))

            # Lower threshold for matching to 30%
            if match_score >= 30:  # include jobs with 30% match
                scored_jobs.append(
                    {
                        "title": f"{job['title']} at {job['company']}",
                        "match_score": f"{match_score}%",
                        "location": job["location"],
                        "salary_range": job["salary_range"],
                        "requirements": job["requirements"],
                    }
                )

        print(f" ==>>> Scored Jobs: {scored_jobs}")
        # Sort by match score
        scored_jobs.sort(key=lambda x: int(x["match_score"].rstrip("%")), reverse=True)

        return {
            "matched_jobs": scored_jobs[:3],
            "match_timestamp": "2024-03-14",
            "number_of_matches": len(scored_jobs),
        }

    def _tokenize(self, text: str) -> set:
        """Normalize and tokenize a skill or requirement string into a set of tokens.

        - Lowercases
        - Replaces common separators with commas
        - Removes punctuation and extraneous characters
        - Returns both full-phrase tokens and word-level tokens for flexible matching
        """
        if not text:
            return set()
        s = text.lower()
        # Normalize common separators
        for sep in ["/", "&", "|", ";", "(", ")", ".", "-", "_"]:
            s = s.replace(sep, ",")
        s = s.replace(" and ", ",")
        parts = [p.strip() for p in re.split(r"[,\n]+", s) if p.strip()]
        tokens = set()
        for part in parts:
            # remove non-alphanumeric except space
            part_clean = re.sub(r"[^a-z0-9 ]+", " ", part).strip()
            if not part_clean:
                continue
            part_clean = " ".join(part_clean.split())
            tokens.add(part_clean)
            # add individual words as tokens
            for w in part_clean.split():
                tokens.add(w)
        return tokens

    def search_jobs(self, skills: list, experience_level: str) -> list:
        """Search jobs based on skills and experience level. Query by experience level in SQL and do tokenized matching in Python for reliability."""
        query = "SELECT * FROM jobs WHERE experience_level = ?"
        params = [experience_level]

        try:
            with sqlite3.connect(self.db.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute(query, params)
                rows = cursor.fetchall()

                candidate_tokens = set()
                # Build candidate tokens from provided skills
                for s in skills:
                    candidate_tokens.update(self._tokenize(s))

                matched = []
                for row in rows:
                    try:
                        reqs = json.loads(row["requirements"]) if row["requirements"] else []
                    except Exception:
                        reqs = []

                    req_tokens = set()
                    for r in reqs:
                        req_tokens.update(self._tokenize(r))

                    # If there are no requirement tokens, skip
                    if not req_tokens:
                        continue

                    # Flexible overlap: count requirement tokens that have a match in candidate tokens
                    overlap = 0
                    for rt in req_tokens:
                        matched_rt = False
                        for ct in candidate_tokens:
                            if rt == ct or rt in ct or ct in rt:
                                matched_rt = True
                                break
                            # check word-level intersection
                            if set(rt.split()).intersection(set(ct.split())):
                                matched_rt = True
                                break
                        if matched_rt:
                            overlap += 1

                    match_pct = (overlap / len(req_tokens)) * 100 if len(req_tokens) > 0 else 0

                    # Include jobs with at least one overlapping token (or configurable threshold)
                    if overlap > 0 or not candidate_tokens:
                        matched.append(
                            {
                                "id": row["id"],
                                "title": row["title"],
                                "company": row["company"],
                                "location": row["location"],
                                "type": row["type"],
                                "experience_level": row["experience_level"],
                                "salary_range": row["salary_range"],
                                "description": row["description"],
                                "requirements": reqs,
                                "benefits": (
                                    json.loads(row["benefits"]) if row["benefits"] else []
                                ),
                                "match_pct": int(round(match_pct)),
                            }
                        )

                # Sort by match_pct descending
                matched.sort(key=lambda j: j.get("match_pct", 0), reverse=True)

                return matched

        except Exception as e:
            print(f"Error searching jobs: {e}")
            return []


