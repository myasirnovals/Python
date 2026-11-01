import os
import sys
from dotenv import load_dotenv

# Prioritaskan load .env di samping .exe jika frozen, atau di direktori kerja/root jika dev
if getattr(sys, "frozen", False):
    exe_dir = os.path.dirname(sys.executable)
    env_path = os.path.join(exe_dir, ".env")
    if os.path.exists(env_path):
        load_dotenv(env_path)
    else:
        load_dotenv()
else:
    load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
