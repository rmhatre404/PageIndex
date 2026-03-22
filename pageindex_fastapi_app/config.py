import os
from pathlib import Path
from dotenv import load_dotenv

# -----------------------------------------------------------------------------
# Determine the project root (the directory containing the .env file)
# We assume the .env file is at D:\PageIndex\.env
# -----------------------------------------------------------------------------
# Get the absolute path of this file's directory (pageindex_fastapi_app)
BASE_DIR = Path(__file__).resolve().parent

# The project root is one level up (PageIndex/)
PROJECT_ROOT = BASE_DIR.parent

# Load environment variables from .env located at the project root
dotenv_path = PROJECT_ROOT / ".env"
if dotenv_path.exists():
    load_dotenv(dotenv_path=dotenv_path)
else:
    # Optionally, also try to load from the current environment
    load_dotenv()

# -----------------------------------------------------------------------------
# API Keys
# -----------------------------------------------------------------------------
PAGEINDEX_API_KEY = os.getenv("PAGEINDEX_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# -----------------------------------------------------------------------------
# Model Configuration
# -----------------------------------------------------------------------------
# The OpenAI model to use for reasoning and final answer
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-5.4-mini-2026-03-17")  # fallback to placeholder
TEMPERATURE = float(os.getenv("TEMPERATURE", "0"))

# -----------------------------------------------------------------------------
# File Paths (derived from project root)
# -----------------------------------------------------------------------------
PDF_PATH = PROJECT_ROOT / "Chapter 1 U.S.-China Economic and Trade Relations.pdf"
TREE_JSON_PATH = PROJECT_ROOT / "knowledge_tree_US-China.json"

# -----------------------------------------------------------------------------
# Application Settings
# -----------------------------------------------------------------------------
STREAMING_MARKER_START = "<STARTOFTEXT>"
STREAMING_MARKER_END = "<ENDOFTEXT>"

# Timeout for document indexing (seconds)
INDEXING_TIMEOUT = int(os.getenv("INDEXING_TIMEOUT", "300"))
# Polling interval for indexing (seconds)
POLL_INTERVAL = int(os.getenv("POLL_INTERVAL", "5"))

# -----------------------------------------------------------------------------
# Validation
# -----------------------------------------------------------------------------
if not PAGEINDEX_API_KEY:
    raise ValueError("PAGEINDEX_API_KEY is not set. Please set it in .env or environment.")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY is not set. Please set it in .env or environment.")