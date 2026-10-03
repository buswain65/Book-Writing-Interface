import sys
import os

# Ensure the root directory (parent of services/) is on sys.path BEFORE loading config
ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import json
import concurrent.futures
from openai import OpenAI
from config import OPENAI_API_KEY, MODEL_NAME

AGENT_PROMPTS = {
    "Publisher": """You are an experienced acquisitions publisher.
Analyze this chapter for commercial viability, hook strength, genre positioning, and marketability.
Format response as JSON with keys: "verdict", "strengths" (list), "market_risks" (list), "recommendations" (list).""",

    "Developmental Editor": """You are a senior developmental editor.
Analyze pacing, narrative flow, character arcs, structural integrity, and logic/plot gaps.
Format response as JSON with keys: "verdict", "pacing_critique", "character_notes", "structural_fixes" (list).""",

    "Fellow Writer": """You are an award-winning fiction author focusing on craft.
Analyze sentence mechanics, dialogue authenticity, show-vs-tell balance, tone, and prose imagery.
Format response as JSON with keys: "verdict", "prose_highlights" (list), "craft_critique" (list), "dialogue_notes".""",

    "Genre Fan": """You are a die-hard enthusiast and avid reader of this book's genre.
Analyze emotional payoffs, trope execution, immersion, character attachment, and satisfaction.
Format response as JSON with keys: "verdict", "favorite_moments" (list), "friction_points" (list), "excitement_rating".""",

    "Genre Skeptic": """You are a general fiction reader who does not usually read this genre.
Analyze accessibility, clarity, logic, lack of jargon, and whether the chapter hooks a casual outsider.
Format response as JSON with keys: "verdict", "confusion_points" (list), "accessible_elements" (list), "outsider_take"."""
}

class AgentEngine:
    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

    def _run_single_agent(self, role: str, prompt: str, text: str, context: str) -> dict:
        if not self.client:
            # Fallback mock response for testing prior to entering API key
            return {
                "role": role,
                "status": "mock",
                "feedback": {
                    "verdict": f"[{role} Mode] Configure your OPENAI_API_KEY in environment or config.py to receive live AI reviews.",
                    "notes": ["Sample feedback point 1", "Sample feedback point 2"]
                }
            }

        user_content = f"STORY CONTEXT:\n{context}\n\nCHAPTER TEXT:\n{text}"
        
        try:
            response = self.client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": prompt},
                    {"role": "user", "content": user_content}
                ],
                response_format={"type": "json_object"},
                temperature=0.7
            )
            data = json.loads(response.choices[0].message.content)
            return {"role": role, "status": "success", "feedback": data}
        except Exception as e:
            return {"role": role, "status": "error", "error": str(e)}

    def run_all_agents(self, text: str, context: str = "") -> dict:
        results = {}
        with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
            future_to_role = {
                executor.submit(self._run_single_agent, role, prompt, text, context): role
                for role, prompt in AGENT_PROMPTS.items()
            }
            for future in concurrent.futures.as_completed(future_to_role):
                role = future_to_role[future]
                results[role] = future.result()
        return results