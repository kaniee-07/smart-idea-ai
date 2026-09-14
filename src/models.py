"""Pydantic models for SmartIdea AI structured output."""

from pydantic import BaseModel, Field, field_validator
from typing import List


class Idea(BaseModel):
    """A single innovation idea with scoring."""

    title: str = Field(description="Concise, compelling title for the idea")
    category: str = Field(description="Category or domain of the idea (e.g., EdTech, HealthTech, SaaS)")
    problem: str = Field(description="The specific problem this idea addresses")
    solution: str = Field(description="Clear description of the proposed solution")
    target_users: str = Field(description="Primary target audience or users")
    innovation: str = Field(description="What makes this idea unique or innovative")
    impact_score: int = Field(description="Impact score from 1 (low) to 10 (transformative)")
    feasibility_score: int = Field(description="Feasibility score from 1 (very hard) to 10 (very easy)")
    why_it_matters: str = Field(description="Why this idea is important and worth pursuing")
    implementation_steps: List[str] = Field(description="Practical step-by-step implementation plan")

    @field_validator("impact_score", "feasibility_score")
    @classmethod
    def validate_score(cls, v: int) -> int:
        if not (1 <= v <= 10):
            raise ValueError(f"Score must be between 1 and 10, got {v}")
        return v

    @property
    def overall_score(self) -> float:
        return round((self.impact_score + self.feasibility_score) / 2, 1)


class IdeaResponse(BaseModel):
    """Full response from the idea generation workflow."""

    detected_domain: str = Field(description="The domain detected from the user's prompt")
    problem_summary: str = Field(description="Concise summary of the core problem or opportunity")
    trends_or_opportunities: List[str] = Field(description="Key trends or opportunities identified")
    ideas: List[Idea] = Field(description="List of generated innovation ideas")
    recommended_idea: str = Field(description="Title of the most recommended idea")
    recommendation_reason: str = Field(description="Detailed reasoning for the recommendation")
