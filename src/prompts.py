"""Prompt templates for SmartIdea AI."""

SYSTEM_PROMPT = """You are an expert innovation strategist, startup ideator, researcher, and product thinker.

Your role is to:
1. Deeply understand the user's objective, domain, and constraints.
2. Identify the problem space and emerging trends or opportunities.
3. Generate genuinely diverse and different ideas - not variations of the same concept.
4. Avoid generic or obvious ideas. Prefer useful, realistic, and innovative ideas.
5. Score each idea on:
   - Impact (1-10): How much positive change or value it creates
   - Feasibility (1-10): How realistic it is to build with available resources
6. Recommend the strongest idea based primarily on Impact + Feasibility while also considering innovation and relevance.
7. Provide a clear, convincing reason for your recommendation.
8. Give practical, actionable implementation steps for each idea.

IMPORTANT: Each idea must address the problem from a genuinely different angle. Variety is essential."""


def build_generation_prompt(prompt: str, domain: str, constraints: str, number_of_ideas: int, has_image: bool) -> str:
    """Build the main idea generation prompt."""
    image_instruction = ""
    if has_image:
        image_instruction = """

IMAGE ANALYSIS:
An image has been uploaded. Please carefully analyze it:
- If it is a product sketch: identify the product concept, components, weaknesses, and improvement opportunities.
- If it is a UI screenshot: identify UX problems, missing features, and improvement opportunities.
- If it is handwritten notes: interpret and organize the content.
- If it is a diagram: understand the components, relationships, and possible improvements.

Use your image analysis to enrich and contextualize the ideas you generate.
"""

    constraints_section = ""
    if constraints and constraints.strip():
        constraints_section = f"""

CONSTRAINTS (must respect these):
{constraints.strip()}
"""

    return f"""TASK: Generate {number_of_ideas} innovation ideas based on the following input.

USER PROMPT:
{prompt.strip()}

DOMAIN: {domain}{constraints_section}{image_instruction}

INSTRUCTIONS:
1. First, identify the core problem or opportunity.
2. Identify key trends or market opportunities in this space.
3. Generate exactly {number_of_ideas} ideas that are:
   - Genuinely different from each other (different angles, business models, technologies, target users)
   - Specific and actionable, not vague
   - Relevant to the domain and constraints
   - Innovative but realistic
4. For each idea, score Impact (1-10) and Feasibility (1-10).
5. Recommend the single strongest idea with a detailed reason.

Return a complete, structured response with all required fields."""


def build_refinement_prompt(idea_dict: dict, instruction: str) -> str:
    """Build the idea refinement prompt."""
    steps = ", ".join(idea_dict.get("implementation_steps", []))
    return f"""TASK: Refine and improve the following idea based on the given instruction.

ORIGINAL IDEA:
Title: {idea_dict.get("title", "")}
Category: {idea_dict.get("category", "")}
Problem: {idea_dict.get("problem", "")}
Solution: {idea_dict.get("solution", "")}
Target Users: {idea_dict.get("target_users", "")}
Innovation: {idea_dict.get("innovation", "")}
Why It Matters: {idea_dict.get("why_it_matters", "")}
Impact Score: {idea_dict.get("impact_score", "")}/10
Feasibility Score: {idea_dict.get("feasibility_score", "")}/10
Implementation Steps: {steps}

REFINEMENT INSTRUCTION:
{instruction.strip()}

INSTRUCTIONS:
- Carefully apply the refinement instruction to improve the idea.
- Update all fields to reflect the refined version.
- Re-score impact and feasibility after refinement.
- Keep what works well; improve what the instruction targets.
- Return a fully updated idea with all required fields."""
