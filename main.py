"""Main entry point for the ColdChain 360 backend API.

All application configuration is in app.py.
Command: uvicorn main:app --host 0.0.0.0 --port 8000
"""

import sys
from pathlib import Path

# Ensure current directory is in sys.path
current_dir = Path(__file__).resolve().parent
if str(current_dir) not in sys.path:
    sys.path.insert(0, str(current_dir))

try:
    from app import app
except ImportError:
    from backend.app import app

__all__ = ["app"]
