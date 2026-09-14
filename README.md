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
User (Browser SPA) 
  → Vercel CDN / Static Frontend (public/index.html + Plotly.js)
  → Vercel Serverless Function (api/index.py via FastAPI)
  → LangChain
  → Google Gemini (gemini-3.6-flash)
  → Structured Ideas & Scoring
  → Plotly Visualizations
  → Interactive Dashboard & Refinement
```

## Project Structure

```
smartidea-ai/
├── api/
│   ├── __init__.py
│   └── index.py            # Vercel Serverless Function (FastAPI API)
├── public/
│   ├── index.html          # Responsive Dark-themed Single Page Application
│   ├── style.css           # Styling & UI components
│   └── app.js              # Client-side state, API calls & Plotly rendering
├── src/
│   ├── __init__.py
│   ├── ai.py               # LangChain + Gemini integration
│   ├── prompts.py          # Innovation prompts & refinement templates
│   ├── models.py           # Pydantic data models (Idea, IdeaResponse)
│   └── visualization.py    # Plotly figures (scatter, category bar, idea map)
├── vercel.json             # Vercel serverless routing configuration
├── requirements.txt        # Dependencies for Vercel serverless deployment
├── run_local.py            # Run the Vercel app locally on http://localhost:8000
├── streamlit_app.py        # Streamlit version for optional local standalone use
├── .env.example            # Environment configuration template
├── .gitignore
└── README.md
```

## Local Development

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

Copy the example file:
```bash
copy .env.example .env
```

Open `.env` and set:
```
GEMINI_API_KEY=YOUR_GEMINI_API_KEY
```

### 4. Run the Vercel-compatible app locally

```bash
python run_local.py
```
Open **http://localhost:8000** in your browser.

*(Optional: To run the legacy Streamlit interface: `streamlit run streamlit_app.py`)*

## Deploying to Vercel

1. Push your code to GitHub:
   ```bash
   git add .
   git commit -m "Deploy to Vercel"
   git push origin main
   ```
2. Go to [vercel.com](https://vercel.com) and click **"Add New..."** → **"Project"**.
3. Import your GitHub repository: `kaniee-07/smart-idea-ai`.
4. In the **Configure Project** screen:
   - **Framework Preset**: Leave as **Other** (or Auto-detected).
   - **Root Directory**: `./` (leave default).
5. Open the **Environment Variables** section:
   - **Key**: `GEMINI_API_KEY`
   - **Value**: Your Gemini API key from Google AI Studio.
   - Click **Add**.
6. Click **Deploy**.
7. Vercel will build and serve your app at `https://<project-name>.vercel.app`.

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
