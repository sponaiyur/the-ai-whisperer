"""File configurations and constants"""
import os
from dotenv import load_dotenv

load_dotenv()

HISTORY_CSV = "prompt_history.csv"
FIELDNAMES = ["prompt", "score"]
MAX_HISTORY_ITEMS=5

API_KEY=os.getenv('GROQ_API_KEY')
MODEL="llama3-70b-8192"
