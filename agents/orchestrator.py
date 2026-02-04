from typing import Dict, Any
from .base_agent import BaseAgent
from .extractor_agent import ExtractorAgent
from .analyzer_agent import AnalyzerAgent
from .matcher_agent import MatcherAgent
from .screener_agent import ScreenerAgent
from .recommender_agent import RecommenderAgent



class OrchestratorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="OrchestratorAgent",
            instructions=("""Coordinate the recruitment workflow and delegate tasks to specialized agents.
            Ensure proper flow of information between extraction, analysis, matching, screening, and recommendation phases.
            Maintain context and aggregate results from each stage."""),
        )
        self.setup_agents()


    def setup_agents(self):
        """Initialize all specialized agents"""
        self.extractor_agent = ExtractorAgent()
        self.analyzer_agent = AnalyzerAgent()
        self.matcher_agent = MatcherAgent()
        self.screener_agent = ScreenerAgent()
        self.recommender_agent = RecommenderAgent()

    async def run(self, messages: list) -> Dict[str, Any]:
        """Process a single message through the agent"""
        prompt = messages[-1]["content"]
        response = self._query_ollama(prompt)
        return self._parse_json_safely(response)

    async def process_application(self, resume_data: Dict[str, Any]) -> Dict[str, Any]:
        """Main workflow orchestrator for processing job applications"""
        print("🎯 Orchestrator: Starting application process")

        workflow_context = {
            "resume_data": resume_data,
            "status": "initiated",
            "current_stage": "extraction"
        }


        try:
            # Extraction Stage
            extracted_data = await self.extractor_agent.run(
                [{"role": "user","content": str(resume_data)}]
            )

            workflow_context.update({
                "extracted_data": extracted_data,
                "current_stage": "analysis"
            })

            # Analysis Stage
            analysis_results = await self.analyzer_agent.run(
                [{"role": "user","content": str(extracted_data)}]
            )
            workflow_context.update({
                "analyzed_data": analysis_results,
                "current_stage": "matching"
            })

            # Matching Stage
            job_matches = await self.matcher_agent.run(
                [{"role": "user","content": str(analysis_results)}]
            )
            workflow_context.update({
                "matched_data": job_matches,
                "current_stage": "screening"
            })
            # Screening Stage (optional)
            if hasattr(self, "screener_agent") and getattr(self, "screener_agent") is not None:
                screening_results = await self.screener_agent.run(
                    [{"role": "user","content": str(job_matches)}]
                )
                workflow_context.update({
                    "screened_data": screening_results,
                    "current_stage": "recommendation"
                })
            else:
                screening_results = job_matches
                workflow_context.update({
                    "screened_data": screening_results,
                    "current_stage": "recommendation"
                })
            # Recommendation Stage (optional)
            if hasattr(self, "recommender_agent") and getattr(self, "recommender_agent") is not None:
                final_recommendation = await self.recommender_agent.run(
                    [{"role": "user","content": str(screening_results)}]
                )
            else:
                final_recommendation = screening_results
            workflow_context.update({
                "recommended_data": final_recommendation,
                "current_stage": "completed",
                "status": "success"
            })

            return workflow_context
        
        except Exception as e:
            workflow_context.update({ "status": "failed", "error": str(e) })
            raise
        



    