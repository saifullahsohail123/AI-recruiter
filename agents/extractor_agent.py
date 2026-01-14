from typing import Dict,Any
from pdfminer.high_level import extract_text # pip install pdfminer.six
from .base_agent import BaseAgent



class ExtractorAgent(BaseAgent):
    def __init__(self):
        super().__init__(
            name="ExtractorAgent",
            instructions=("""Extract and structure information from resumes.
                          You will receive raw text extracted from a resume PDF.
                          Your task is to identify key sections such as Contact Information,
                          Education, Work Experience, Skills, and Certifications.
                          Return the extracted information in a JSON format with appropriate fields.""")
        )


    async def run(self, messages: list) -> Dict[str, Any]:
            """Process the resume and extract information"""
            print("ExtractorAgent: Starting extraction process...")
            
            resume_data = eval(messages[-1]["content"])
            # Extract text from PDF
            if resume_data.get("file_path"):
                print(f"ExtractorAgent: Extracting text from {resume_data['file_path']}...")
                raw_text = extract_text(resume_data["file_path"])
            else:
                raw_text = resume_data.get("text", "")
            
            # Get structured information from Ollama
            extracted_info = self._query_ollama(raw_text)

            return {
                 "raw_text": raw_text,
                 "structured_data": extracted_info,
                 "extraction_status": "completed"
            }

    