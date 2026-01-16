import os
import json
import logging
from openai import OpenAI
from typing import Dict, Any, Union
from config import OPENAI_API_KEY, OPENAI_MODEL, OPENAI_MAX_TOKENS, DAILY_ANALYSIS_PROMPT, WEEKLY_ANALYSIS_PROMPT

# Configure logging
logger = logging.getLogger(__name__)

# Initialize client only if key is present to avoid immediate crash on import
if OPENAI_API_KEY:
    client = OpenAI(api_key=OPENAI_API_KEY)
else:
    client = None

class AIAnalyzer:
    def _call_openai(self, prompt: str) -> Union[Dict[str, Any], str]:
        """Helper to call OpenAI and parse JSON response."""
        if not client:
            return {"error": "API Key Missing", "message": "OPENAI_API_KEY not found in environment variables."}
            
        try:
            try:
                # New version
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    max_completion_tokens=OPENAI_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
            except TypeError:
                # Old version fallback
                response = client.chat.completions.create(
                    model=OPENAI_MODEL,
                    max_tokens=OPENAI_MAX_TOKENS,
                    messages=[{"role": "user", "content": prompt}]
                )
            
            content = response.choices[0].message.content
            
            # Attempt to parse JSON
            try:
                # simple cleanup if model returns markdown ticks
                cleaned_content = content.replace("```json", "").replace("```", "").strip()
                return json.loads(cleaned_content)
            except json.JSONDecodeError:
                logger.error(f"Failed to parse JSON: {content}")
                return {"error": "Parsing Error", "raw_content": content, "message": "AI returned unstructured text."}
                
        except Exception as e:
            logger.error(f"OpenAI API Error: {e}")
            return {"error": "API Error", "message": str(e)}

    def analyze_daily(self, data: Dict) -> Dict[str, Any]:
        """Analyze a single day's data returning structured JSON."""
        prompt = DAILY_ANALYSIS_PROMPT.format(data=str(data))
        return self._call_openai(prompt)

    def analyze_weekly(self, data: Dict) -> Dict[str, Any]:
        """Analyze multiple days of data returning structured JSON."""
        prompt = WEEKLY_ANALYSIS_PROMPT.format(data=str(data))
        return self._call_openai(prompt)
