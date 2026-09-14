"""Local development server for SmartIdea AI (Vercel-compatible app)."""

import uvicorn
import os
import sys
from pathlib import Path

# Ensure root directory is in sys.path
ROOT_DIR = Path(__file__).resolve().parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

if __name__ == "__main__":
    print("=" * 60)
    print("  SmartIdea AI - Vercel App Local Server")
    print("  Local URL: http://localhost:8000")
    print("  API Docs:  http://localhost:8000/docs")
    print("=" * 60)
    uvicorn.run("api.index:app", host="127.0.0.1", port=8000, reload=True)
