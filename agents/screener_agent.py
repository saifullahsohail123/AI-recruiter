from typing import Dict, Any
from .base_agent import BaseAgent


class ScreenerAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name ="ScreenerAgent",
            instructions="""Screen candidates based on:
            - Qualification alignment
            - Experience relevance
            - Skill match percentage
            - Cultural fit indicators
            - Red flags or concerns
            Provide comprehensive screening reports.""",
        )

    async def run(self, messages: list) -> Dict[str, Any]:
        """Screen the candidate"""
        print("👥 Screener: Conducting initial screening")

        workflow_context =  eval(messages[-1]["content"]) # Assume content is a dict
        screening_results = self._query_ollama(str(workflow_context)) # Convert dict to string for querying

        return {
            "screening_results": screening_results,
            "screening_status": "2024-03-14",
            "screening_score": 85,  # Placeholder score
        }
    # End of ScreenerAgent class

