"""AI integration: LangChain + Google Gemini for SmartIdea AI."""

import os
import base64
import json
from typing import Optional

from dotenv import load_dotenv
from PIL import Image
import io

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage

from src.models import Idea, IdeaResponse
from src.prompts import SYSTEM_PROMPT, build_generation_prompt, build_refinement_prompt

# Load environment variables
load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")


class ConfigurationError(Exception):
    """Raised when the app is misconfigured."""
    pass


class AIGenerationError(Exception):
    """Raised when AI generation fails."""
    pass


def _get_llm(structured_output_model=None):
    """Initialize and return the Gemini LLM."""
    if not GEMINI_API_KEY:
        raise ConfigurationError(
            "Gemini API key is missing. Please create a .env file and add: GEMINI_API_KEY=your_key_here"
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.6-flash",
        google_api_key=GEMINI_API_KEY,
        temperature=0.8,
        max_retries=2,
    )

    if structured_output_model:
        return llm.with_structured_output(structured_output_model)

    return llm


def _image_to_base64(image: Image.Image):
    """Convert a PIL Image to base64 string, returns (base64_str, media_type)."""
    if image.mode not in ("RGB", "L"):
        image = image.convert("RGB")

    buffer = io.BytesIO()
    image.save(buffer, format="JPEG")
    buffer.seek(0)
    b64 = base64.b64encode(buffer.read()).decode("utf-8")
    return b64, "image/jpeg"


def _build_messages(system_prompt: str, user_prompt: str, image=None):
    """Build LangChain messages, optionally including an image."""
    system_message = SystemMessage(content=system_prompt)

    if image is not None:
        b64_image, media_type = _image_to_base64(image)
        human_content = [
            {"type": "text", "text": user_prompt},
            {
                "type": "image_url",
                "image_url": {"url": f"data:{media_type};base64,{b64_image}"},
            },
        ]
    else:
        human_content = user_prompt

    human_message = HumanMessage(content=human_content)
    return [system_message, human_message]


def _parse_response_text(text: str) -> dict:
    """Try to extract JSON from LLM text response."""
    text = text.strip()

    if "```json" in text:
        start = text.find("```json") + 7
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()
    elif "```" in text:
        start = text.find("```") + 3
        end = text.find("```", start)
        if end > start:
            text = text[start:end].strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError as e:
        raise AIGenerationError(f"Failed to parse AI response as JSON: {e}")


JSON_SCHEMA_FULL = """

IMPORTANT: Respond ONLY with valid JSON matching this exact schema (no markdown, no explanation outside JSON):
{
  "detected_domain": "string",
  "problem_summary": "string",
  "trends_or_opportunities": ["string", "..."],
  "ideas": [
    {
      "title": "string",
      "category": "string",
      "problem": "string",
      "solution": "string",
      "target_users": "string",
      "innovation": "string",
      "impact_score": 7,
      "feasibility_score": 8,
      "why_it_matters": "string",
      "implementation_steps": ["string", "..."]
    }
  ],
  "recommended_idea": "string",
  "recommendation_reason": "string"
}"""


JSON_SCHEMA_IDEA = """

IMPORTANT: Respond ONLY with valid JSON matching this exact schema:
{
  "title": "string",
  "category": "string",
  "problem": "string",
  "solution": "string",
  "target_users": "string",
  "innovation": "string",
  "impact_score": 7,
  "feasibility_score": 8,
  "why_it_matters": "string",
  "implementation_steps": ["string", "..."]
}"""


def generate_ideas(
    prompt: str,
    domain: str,
    constraints: str,
    number_of_ideas: int,
    image=None,
) -> IdeaResponse:
    """
    Generate innovation ideas using Gemini through LangChain.

    Args:
        prompt: The user problem/opportunity description.
        domain: Selected domain.
        constraints: Optional constraints string.
        number_of_ideas: Number of ideas (5, 8, or 10).
        image: Optional PIL Image for multimodal context.

    Returns:
        IdeaResponse with structured ideas and recommendation.
    """
    if not prompt or not prompt.strip():
        raise ValueError("Prompt cannot be empty.")

    if number_of_ideas not in (5, 8, 10):
        raise ValueError("Number of ideas must be 5, 8, or 10.")

    user_prompt = build_generation_prompt(
        prompt=prompt,
        domain=domain,
        constraints=constraints,
        number_of_ideas=number_of_ideas,
        has_image=(image is not None),
    )

    # Try structured output first
    try:
        llm = _get_llm(structured_output_model=IdeaResponse)
        messages = _build_messages(SYSTEM_PROMPT, user_prompt, image)
        result = llm.invoke(messages)
        if isinstance(result, IdeaResponse):
            return result
    except ConfigurationError:
        raise
    except Exception:
        pass

    # Fallback: text generation + JSON parsing
    try:
        llm = _get_llm()
        json_prompt = user_prompt + JSON_SCHEMA_FULL
        messages = _build_messages(SYSTEM_PROMPT, json_prompt, image)
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        data = _parse_response_text(raw_text)
        return IdeaResponse(**data)
    except ConfigurationError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise AIGenerationError(f"Idea generation failed: {str(e)}")


def refine_idea(idea: Idea, refinement_instruction: str) -> Idea:
    """
    Refine an existing idea based on a user instruction.

    Args:
        idea: The Idea object to refine.
        refinement_instruction: Natural language refinement instruction.

    Returns:
        An improved Idea object.
    """
    if not refinement_instruction or not refinement_instruction.strip():
        raise ValueError("Refinement instruction cannot be empty.")

    idea_dict = idea.model_dump()
    user_prompt = build_refinement_prompt(idea_dict, refinement_instruction)

    refine_system = "You are an expert product designer and innovation strategist. Refine ideas thoughtfully and specifically based on the given instruction."

    # Try structured output first
    try:
        llm = _get_llm(structured_output_model=Idea)
        messages = _build_messages(refine_system, user_prompt)
        result = llm.invoke(messages)
        if isinstance(result, Idea):
            return result
    except ConfigurationError:
        raise
    except Exception:
        pass

    # Fallback: text generation + JSON parsing
    try:
        llm = _get_llm()
        json_prompt = user_prompt + JSON_SCHEMA_IDEA
        messages = _build_messages(refine_system, json_prompt)
        response = llm.invoke(messages)
        raw_text = response.content if hasattr(response, "content") else str(response)
        data = _parse_response_text(raw_text)
        return Idea(**data)
    except ConfigurationError:
        raise
    except ValueError:
        raise
    except Exception as e:
        raise AIGenerationError(f"Idea refinement failed: {str(e)}")
