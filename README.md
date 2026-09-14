# SmartIdea AI

**Your AI-powered innovation companion**

## Problem Statement

Individuals, startups, and researchers often struggle to generate diverse, high-quality ideas around a given challenge. SmartIdea AI solves this by leveraging Google Gemini through LangChain to generate structured, scored, and contextually relevant ideas from a simple text prompt, with optional image understanding for richer context.

## Features

- **Text-to-Ideas**: Describe your problem and get multiple structured ideas instantly.
- **Domain Selection**: Startup, Research, Product, Education, Healthcare, Sustainability, Technology, and more.
- **Constraints Support**: Budget, audience, or tech constraints that shape the ideas.
- **Multimodal Image Input**: Upload PNG/JPG/JPEG (product sketch, UI screenshot, handwritten notes, diagram).
- **Structured Output**: Each idea has title, category, problem, solution, target users, innovation angle, implementation steps.
- **Scoring**: Impact (1-10) and Feasibility (1-10) with an overall score.
- **Recommendation**: Gemini recommends the strongest idea with reasoning.
- **Visualizations**: Impact vs Feasibility scatter, category bar chart, idea map.
- **Idea Refinement**: Select any idea and give a refinement instruction.

## Architecture

```
User -> Streamlit UI -> Input Processing -> LangChain -> Google Gemini -> Structured Ideas -> Scoring -> Recommendation -> Dashboard
```

## Project Structure

```
smartidea-ai/
├── app.py               # Streamlit application entry point
├── requirements.txt     # Python dependencies
├── .env.example         # Example environment configuration
├── .gitignore
├── README.md
└── src/
    ├── __init__.py
    ├── ai.py            # LangChain + Gemini integration
    ├── prompts.py       # Prompt templates
    ├── models.py        # Pydantic data models
    └── visualization.py # Plotly chart functions
```

## Installation

### 1. Set up a virtual environment

```bash
python -m venv .venv
```

**Windows:**
```bash
.venv\Scripts\activate
```

**macOS/Linux:**
```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Configure your API key

```bash
copy .env.example .env
```

Open `.env` and replace the placeholder:
```
GEMINI_API_KEY=YOUR_ACTUAL_GEMINI_API_KEY
```

Get your key from https://aistudio.google.com/app/apikey

### 4. Run the application

```bash
streamlit run app.py
```

The app opens at http://localhost:8501

## Example Prompt

> "I want to build an AI-powered solution that helps college students manage their academic workload."

Try domain: **Education**, constraints: **Low budget, mobile-first**, ideas: **8**

## Image Input

| Image Type | What Gemini Extracts |
|---|---|
| Product sketch | Components, weaknesses, opportunities |
| UI screenshot | UX problems, missing features |
| Handwritten notes | Interprets and organizes content |
| Diagram | Components, relationships, improvements |

## Idea Refinement

After generating ideas, use the **Refine an Idea** section:

- "Make this cheaper"
- "Make this suitable for rural India"
- "Add AI features"
- "Turn this into a startup"
- "Make this suitable for a research project"

## Technology Stack

| Layer | Technology |
|---|---|
| UI | Streamlit |
| AI Orchestration | LangChain |
| LLM | Google Gemini (gemini-1.5-flash) |
| Structured Output | Pydantic v2 |
| Visualization | Plotly |
| Image Processing | Pillow |
| Config | python-dotenv |

## Limitations

- Requires a valid Gemini API key (free tier available).
- No persistent storage - ideas are session-only.
- No authentication or multi-user support.
- Image understanding quality depends on image clarity.
- API rate limits apply based on your Gemini plan.
