import os
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file if present
load_dotenv()

# Use relative base directory so it works on both Windows and Linux Cloud instances
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")

# Retrieve API Key from .env first, then st.secrets (for cloud deployment)
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or getattr(st, "secrets", {}).get("OPENAI_API_KEY", "")
MODEL_NAME = os.getenv("LLM_MODEL") or getattr(st, "secrets", {}).get("LLM_MODEL", "gpt-4o")

# Demographic Classification Thresholds
AGE_BRACKETS = {
    "Middle Grade (Ages 8-12)": {"max_grade": 6.5, "target_words_per_sent": 12},
    "Young Adult (Ages 12-18)": {"max_grade": 9.5, "target_words_per_sent": 16},
    "New Adult (Ages 18-25)":   {"max_grade": 11.5, "target_words_per_sent": 20},
    "Adult (Ages 25+)":         {"max_grade": 99.0, "target_words_per_sent": 25}
}
