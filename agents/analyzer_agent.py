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
        structured = extracted_data.get("structured_data", {})
        
        print(f"AnalyzerAgent: Received structured data keys: {list(structured.keys())}")

        # Get structured analysis from Ollama
        analysis_prompt = f"""Analyze this structured resume data and return a JSON object with ONLY these fields:

{{
  "technical_skills": ["skill1", "skill2", ...all skills found],
  "years_of_experience": NUMBER,
  "education": {{
    "degree": "Bachelor/Master/PhD/Diploma or degree name",
    "institution": "University or school name",
    "graduation_year": YYYY
  }},
  "experience_level": "Entry-level/Mid-level/Senior-level",
  "key_achievements": ["achievement1", "achievement2", ...all achievements found],
  "domain_expertise": ["domain1", "domain2", ...all domains found]
}}

Resume Data:
{json.dumps(structured, indent=2)}

IMPORTANT:
- Extract ALL technical skills mentioned (programming languages, frameworks, tools, databases, etc.)
- Extract ALL domains/industries mentioned (AI, web development, data science, etc.)
- Extract years of experience as a number
- Extract first education entry if multiple exist
- Return ONLY valid JSON, no markdown, no extra text
"""

        analysis_results = self._query_ollama(analysis_prompt)
        
        print(f"AnalyzerAgent: Raw Ollama response (first 200 chars): {analysis_results[:200]}")
        
        parsed_results = self._parse_json_safely(analysis_results)
        
        print(f"AnalyzerAgent: Parsed result keys: {list(parsed_results.keys()) if isinstance(parsed_results, dict) else 'not a dict'}")

        # Ensure we have valid data even if parsing fails
        if "error" in parsed_results:
            print(f"AnalyzerAgent: Parsing error detected, using defaults")
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