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
            
            # Get structured information from Ollama with explicit prompt
            extraction_prompt = f"""Extract and structure all information from this resume. Return ONLY a valid JSON object with these fields:

{{
  "contact_info": {{
    "name": "...",
    "email": "...",
    "phone": "..."
  }},
  "summary": "...",
  "technical_skills": ["skill1", "skill2", ...],
  "education": [
    {{
      "degree": "...",
      "field_of_study": "...",
      "institution": "...",
      "graduation_year": YYYY
    }}
  ],
  "work_experience": [
    {{
      "title": "...",
      "company": "...",
      "duration": "...",
      "responsibilities": ["...", "..."]
    }}
  ],
  "certifications": ["cert1", "cert2", ...],
  "domain_expertise": ["domain1", "domain2", ...],
  "years_of_experience": NUMBER
}}

Resume Text:
{raw_text}

Return ONLY the JSON object, no markdown formatting, no extra text.
"""
            extracted_info = self._query_ollama(extraction_prompt)
            
            # Try to parse and validate
            import json
            try:
                parsed = json.loads(extracted_info)
                print(f"ExtractorAgent: Successfully extracted and parsed resume data")
                structured_data = parsed
            except json.JSONDecodeError:
                print(f"ExtractorAgent: JSON parsing failed, attempting fallback parse")
                structured_data = self._parse_json_safely(extracted_info)

            return {
                 "raw_text": raw_text,
                 "structured_data": structured_data,
                 "extraction_status": "completed"
            }

    