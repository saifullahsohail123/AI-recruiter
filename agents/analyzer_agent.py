from .base_agent import BaseAgent
from typing import Dict, Any
import json


class AnalyzerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="AnalyzerAgent",
            instructions=("""Analyze the structured resume data extracted by the ExtractorAgent.
                          Your task is to evaluate the candidate's qualifications, experience,
                          and skills in relation to the job requirements.
                          Provide insights on strengths, weaknesses, and overall suitability
                          for the role in a JSON format.""")
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Analyze the structured resume data"""
        print("AnalyzerAgent: Starting analysis process...")
        
        extracted_data = eval(messages[-1]["content"])


        # Get structured analysis from Ollama
        analysis_prompt = f"""
        Analyze this resume data and return a JSON object with the following structure:

        {{
        "technical_skills": [...],
        "years_of_experience": 0,
        "education":{{"degree": "...", "institution": "...", "graduation_year": 0
        }}
        "experience_level": "...",
        "key_achievements": [...],
        "domain_expertise": ["domain1", "domain2", "..."],
        }}

        Resume Data:
        {extracted_data["structured_data"]}

        Return only the JSON object. no other text.
        """

        analysis_results = self._query_ollama(analysis_prompt)
        
        parsed_results = self._parse_json_safely(analysis_results)

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            parsed_results = {
                "technical_skills": [],
                "years_of_experience": 0,
                "education": {"degree": "Unknown", "institution": "Unknown", "graduation_year": 0},
                "experience_level": "",
                "key_achievements": [],
                "domain_expertise": []
            }
        
        return {
            "skills_analysis": parsed_results,
            "analysis_timestamp": "2023-10-01T12:00:00Z",
            "confidence_score": 0.85 if "error" not in parsed_results else 0.5,
        }