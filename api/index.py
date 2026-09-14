"""Vercel Serverless Function entrypoint for SmartIdea AI."""

import os
import sys
import io
import base64
import json
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from PIL import Image

# Ensure project root is in sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

# Load local environment variables if present
load_dotenv(ROOT_DIR / ".env")

from src.models import Idea, IdeaResponse
from src.ai import generate_ideas, refine_idea, ConfigurationError, AIGenerationError
from src.visualization import (
    impact_vs_feasibility_chart,
    category_distribution_chart,
    idea_map_chart,
)

app = FastAPI(
    title="SmartIdea AI API",
    description="Vercel Serverless API for SmartIdea AI",
    version="1.0.0",
)

# Enable CORS for local dev and web clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class GenerateRequest(BaseModel):
    prompt: str
    domain: str = "Technology"
    constraints: Optional[str] = ""
    number_of_ideas: int = 5
    image_base64: Optional[str] = None


class RefineRequest(BaseModel):
    idea: Idea
    refinement_instruction: str


@app.get("/api/health")
def health_check():
    """Health check endpoint to verify API and configuration status."""
    has_key = bool(os.getenv("GEMINI_API_KEY"))
    return {
        "status": "ok",
        "api_key_configured": has_key,
        "message": "Ready" if has_key else "Gemini API key is not configured in environment",
    }


@app.post("/api/generate")
def api_generate(req: GenerateRequest):
    """Generate innovation ideas and interactive visualization data."""
    if not req.prompt or not req.prompt.strip():
        raise HTTPException(status_code=400, detail="Please provide an idea or problem prompt.")

    if req.number_of_ideas not in (5, 8, 10):
        raise HTTPException(status_code=400, detail="Number of ideas must be 5, 8, or 10.")

    pil_image = None
    if req.image_base64:
        try:
            b64_str = req.image_base64
            if "," in b64_str:
                b64_str = b64_str.split(",", 1)[1]
            img_bytes = base64.b64decode(b64_str)
            pil_image = Image.open(io.BytesIO(img_bytes))
            pil_image.verify()
            pil_image = Image.open(io.BytesIO(img_bytes))
        except Exception:
            pil_image = None  # Gracefully fall back to text-only

    try:
        result = generate_ideas(
            prompt=req.prompt,
            domain=req.domain,
            constraints=req.constraints or "",
            number_of_ideas=req.number_of_ideas,
            image=pil_image,
        )

        # Generate Plotly charts as JSON data
        scatter_fig = impact_vs_feasibility_chart(result.ideas)
        category_fig = category_distribution_chart(result.ideas)
        map_fig = idea_map_chart(result.ideas, central_topic=result.detected_domain)

        charts_data = {
            "scatter": json.loads(scatter_fig.to_json()),
            "category": json.loads(category_fig.to_json()),
            "map": json.loads(map_fig.to_json()),
        }

        return {
            "success": True,
            "data": result.model_dump(),
            "charts": charts_data,
        }
    except ConfigurationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during generation. Please verify your GEMINI_API_KEY.",
        )


@app.post("/api/refine")
def api_refine(req: RefineRequest):
    """Refine a specific idea using Gemini."""
    if not req.refinement_instruction or not req.refinement_instruction.strip():
        raise HTTPException(status_code=400, detail="Refinement instruction cannot be empty.")

    try:
        refined = refine_idea(req.idea, req.refinement_instruction)
        return {
            "success": True,
            "data": refined.model_dump(),
        }
    except ConfigurationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except AIGenerationError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="An unexpected error occurred during refinement.",
        )


# Mount public folder for local execution (when not running inside Vercel)
if not os.getenv("VERCEL"):
    public_path = ROOT_DIR / "public"
    if public_path.exists():
        app.mount("/", StaticFiles(directory=str(public_path), html=True), name="static")
