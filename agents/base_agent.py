from typing import Dict, Any
import json
from openai import OpenAI



class BaseAgent:
    def __init__(self,name: str, instructions: str):
        self.name = name
        self.instructions = instructions
        self.ollama_client = OpenAI(
            base_url="http://localhost:11434/v1",  # Example base URL for Ollama
            api_key="ollama"  # Ollama may not require an API key
        )
    
    async def run(self, message: list) -> Dict[str, Any]:
        """ Default run method to be overridden by child classes """
        raise NotImplementedError("Subclasses must implement run()")
    
    def _query_ollama(self, prompt: str) -> str:
        """ Query Ollama with the following prompt """
        try:
            response = self.ollama_client.chat.completions.create(
                model="llama2",  # Example model name
                messages=[
                    {"role": "system", "content": self.instructions},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.7,
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error querying Ollama: {e}")
            raise

    def _parse_json_safely(self, text: str) -> Dict[str, Any]:
        """Safely parse JSON from text, handling potential errors"""
        try:
            # Try to find JSON-like content between curly braces
            start = text.find("{")
            end = text.rfind("}")
            if start != -1 and end != -1:
                json_str = text[start:end + 1]
                return json.loads(json_str)
            else:
                return {"error": "No JSON content found"}
        except json.JSONDecodeError:
            return {"error": "Invalid JSON format"}



