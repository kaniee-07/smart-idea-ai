"""SmartIdea AI - Streamlit Application."""

import streamlit as st
from PIL import Image

from src.ai import generate_ideas, refine_idea, ConfigurationError, AIGenerationError
from src.models import IdeaResponse, Idea
from src.visualization import impact_vs_feasibility_chart, category_distribution_chart, idea_map_chart

# --- Page Config ---
st.set_page_config(
    page_title="SmartIdea AI",
    page_icon="💡",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Custom CSS ---
st.markdown("""
<style>
.stApp { background-color: #0a0f1e; }
.main-header { text-align: center; padding: 2rem 0 1rem; }
.main-title {
    font-size: 3rem; font-weight: 800;
    background: linear-gradient(135deg, #6366f1, #8b5cf6, #22d3ee);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;
    margin-bottom: 0.25rem;
}
.main-subtitle { color: #94a3b8; font-size: 1.15rem; margin-top: 0; }
.idea-category {
    display: inline-block; background: #312e81; color: #a5b4fc;
    font-size: 0.75rem; font-weight: 600; padding: 0.2rem 0.6rem;
    border-radius: 999px; margin-bottom: 0.75rem;
}
.rec-card {
    background: linear-gradient(135deg, #1e1b4b, #1e293b);
    border: 1.5px solid #6366f1; border-radius: 14px;
    padding: 1.75rem; margin-bottom: 1.5rem;
}
.rec-title { font-size: 1.5rem; font-weight: 700; color: #a5b4fc; margin-bottom: 0.5rem; }
.section-header {
    font-size: 1.5rem; font-weight: 700; color: #f1f5f9;
    margin: 2rem 0 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #334155;
}
.opportunity-badge {
    display: inline-block; background: #0c4a6e; color: #7dd3fc;
    font-size: 0.85rem; padding: 0.3rem 0.7rem; border-radius: 8px; margin: 0.2rem;
}
</style>
""", unsafe_allow_html=True)

# --- Session State ---
if "result" not in st.session_state:
    st.session_state.result = None
if "refined_idea" not in st.session_state:
    st.session_state.refined_idea = None

# --- Sidebar ---
with st.sidebar:
    st.markdown("## SmartIdea AI")
    st.markdown("*Configure your idea generation*")
    st.divider()

    prompt = st.text_area(
        "Idea / Problem Prompt",
        placeholder="Describe your problem or opportunity...\n\nExample: I want to build an AI-powered solution that helps college students manage their academic workload.",
        height=140,
        help="Describe the problem you want to solve or the opportunity you want to explore.",
    )

    domain = st.selectbox(
        "Domain",
        ["Startup", "Research", "Product", "Content Creation", "Education",
         "Healthcare", "Sustainability", "Technology", "Other"],
        help="Select the domain most relevant to your idea.",
    )

    constraints = st.text_area(
        "Constraints (Optional)",
        placeholder="E.g., Low budget, mobile-first, rural users, no internet required...",
        height=80,
        help="Add any constraints that should shape the ideas.",
    )

    number_of_ideas = st.selectbox(
        "Number of Ideas",
        [5, 8, 10],
        help="How many ideas should be generated?",
    )

    uploaded_file = st.file_uploader(
        "Upload Image (Optional)",
        type=["png", "jpg", "jpeg"],
        help="Upload a product sketch, UI screenshot, handwritten notes, or diagram.",
    )

    st.divider()
    generate_btn = st.button("Generate Ideas", use_container_width=True, type="primary")

# --- Main Header ---
st.markdown("""
<div class="main-header">
    <div class="main-title">SmartIdea AI</div>
    <div class="main-subtitle">Your AI-powered innovation companion</div>
</div>
""", unsafe_allow_html=True)

# --- Welcome State ---
if st.session_state.result is None and not generate_btn:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("### How It Works")
        st.markdown("""
1. **Describe** your problem or opportunity in the sidebar.
2. **Select** a domain and optionally add constraints.
3. **Upload** an image for richer context (optional).
4. **Generate** structured, scored ideas instantly.
5. **Refine** any idea with a natural language instruction.
        """)
    with col2:
        st.markdown("### What You Get")
        st.markdown("""
- Structured ideas with problem, solution, and target users
- Impact & Feasibility scores (1–10)
- Overall score and AI recommendation
- Interactive visualizations
- Practical implementation steps
        """)
    with col3:
        st.markdown("### Tips")
        st.markdown("""
- Be specific in your prompt for better ideas
- Use constraints to guide realistic ideas
- Upload a sketch or diagram for multimodal analysis
- Use refinement to adapt ideas to your context
        """)

# --- Generate ---
if generate_btn:
    if not prompt or not prompt.strip():
        st.error("Please enter a prompt before generating ideas.")
    else:
        pil_image = None
        if uploaded_file is not None:
            try:
                pil_image = Image.open(uploaded_file)
                pil_image.verify()
                uploaded_file.seek(0)
                pil_image = Image.open(uploaded_file)
            except Exception:
                st.warning("The uploaded image could not be read and will be ignored. Proceeding with text-only generation.")
                pil_image = None

        with st.spinner("Analyzing your idea and generating innovations with Gemini..."):
            try:
                result = generate_ideas(
                    prompt=prompt,
                    domain=domain,
                    constraints=constraints,
                    number_of_ideas=number_of_ideas,
                    image=pil_image,
                )
                st.session_state.result = result
                st.session_state.refined_idea = None
                st.rerun()
            except ConfigurationError as e:
                st.error(f"Configuration Error: {e}")
            except ValueError as e:
                st.error(f"Input Error: {e}")
            except AIGenerationError as e:
                st.error(f"Generation Error: {e}")
            except Exception:
                st.error("An unexpected error occurred. Please try again.")

# --- Display Results ---
if st.session_state.result is not None:
    result: IdeaResponse = st.session_state.result
    ideas = result.ideas

    # Innovation Report
    st.markdown('<div class="section-header">Innovation Report</div>', unsafe_allow_html=True)
    col_a, col_b = st.columns([1, 2])
    with col_a:
        st.markdown(f"**Detected Domain:** `{result.detected_domain}`")
        st.markdown("**Problem Summary:**")
        st.info(result.problem_summary)
    with col_b:
        st.markdown("**Key Opportunities:**")
        for opp in result.trends_or_opportunities:
            st.markdown(f'<span class="opportunity-badge">{opp}</span>', unsafe_allow_html=True)
        st.markdown("")

    # Recommended Idea
    recommended = next((i for i in ideas if i.title == result.recommended_idea), ideas[0] if ideas else None)
    st.markdown('<div class="section-header">Recommended Idea</div>', unsafe_allow_html=True)
    if recommended:
        st.markdown(f"""
<div class="rec-card">
    <div class="rec-title">🏆 {recommended.title}</div>
    <p><strong>Category:</strong> {recommended.category}</p>
    <p><strong>Recommendation Reason:</strong> {result.recommendation_reason}</p>
</div>
""", unsafe_allow_html=True)
        m1, m2, m3 = st.columns(3)
        m1.metric("Impact", f"{recommended.impact_score}/10")
        m2.metric("Feasibility", f"{recommended.feasibility_score}/10")
        m3.metric("Overall Score", f"{recommended.overall_score}/10")

    # All Ideas
    st.markdown(f'<div class="section-header">Generated Ideas ({len(ideas)})</div>', unsafe_allow_html=True)
    for idx, idea in enumerate(ideas, start=1):
        is_rec = idea.title == result.recommended_idea
        label = f"Idea #{idx} — {idea.title}" + (" ⭐" if is_rec else "")
        with st.expander(label, expanded=(idx == 1)):
            cols = st.columns([2, 1])
            with cols[0]:
                st.markdown(f'<span class="idea-category">{idea.category}</span>', unsafe_allow_html=True)
                st.markdown("**Problem**")
                st.markdown(idea.problem)
                st.markdown("**Solution**")
                st.markdown(idea.solution)
                st.markdown("**Target Users**")
                st.markdown(idea.target_users)
                st.markdown("**What Makes It Innovative**")
                st.markdown(idea.innovation)
                st.markdown("**Why It Matters**")
                st.markdown(idea.why_it_matters)
            with cols[1]:
                st.metric("Impact", f"{idea.impact_score}/10")
                st.metric("Feasibility", f"{idea.feasibility_score}/10")
                st.metric("Overall", f"{idea.overall_score}/10")
            st.markdown("**Implementation Steps**")
            for step_num, step in enumerate(idea.implementation_steps, start=1):
                st.markdown(f"{step_num}. {step}")

    # Visualizations
    st.markdown('<div class="section-header">Visualizations</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)
    with chart_col1:
        st.plotly_chart(impact_vs_feasibility_chart(ideas), use_container_width=True)
    with chart_col2:
        st.plotly_chart(category_distribution_chart(ideas), use_container_width=True)
    st.plotly_chart(idea_map_chart(ideas, central_topic=result.detected_domain), use_container_width=True)

    # Refine an Idea
    st.markdown('<div class="section-header">Refine an Idea</div>', unsafe_allow_html=True)
    idea_titles = [idea.title for idea in ideas]
    selected_title = st.selectbox("Select an Idea to Refine", idea_titles)
    refinement_instruction = st.text_area(
        "How would you like to refine this idea?",
        placeholder="Examples:\n• Make this cheaper\n• Make this suitable for rural India\n• Add AI features\n• Turn this into a startup\n• Make this suitable for a research project",
        height=100,
    )
    refine_btn = st.button("Refine Idea", type="primary")

    if refine_btn:
        if not refinement_instruction or not refinement_instruction.strip():
            st.error("Please enter a refinement instruction.")
        else:
            selected_idea = next((i for i in ideas if i.title == selected_title), None)
            if selected_idea:
                with st.spinner("Refining your idea with Gemini..."):
                    try:
                        refined = refine_idea(selected_idea, refinement_instruction)
                        st.session_state.refined_idea = refined
                    except ConfigurationError as e:
                        st.error(f"Configuration Error: {e}")
                    except ValueError as e:
                        st.error(f"Input Error: {e}")
                    except AIGenerationError as e:
                        st.error(f"Refinement Error: {e}")
                    except Exception:
                        st.error("An unexpected error occurred during refinement. Please try again.")

    if st.session_state.refined_idea is not None:
        refined: Idea = st.session_state.refined_idea
        st.markdown("---")
        st.markdown("#### Refined Idea Result")
        st.markdown(f'<span class="idea-category">{refined.category}</span>', unsafe_allow_html=True)
        r_col1, r_col2 = st.columns([2, 1])
        with r_col1:
            st.markdown(f"**{refined.title}**")
            st.markdown("**Problem**"); st.markdown(refined.problem)
            st.markdown("**Solution**"); st.markdown(refined.solution)
            st.markdown("**Target Users**"); st.markdown(refined.target_users)
            st.markdown("**What Makes It Innovative**"); st.markdown(refined.innovation)
            st.markdown("**Why It Matters**"); st.markdown(refined.why_it_matters)
            st.markdown("**Implementation Steps**")
            for i, step in enumerate(refined.implementation_steps, 1):
                st.markdown(f"{i}. {step}")
        with r_col2:
            st.metric("Impact", f"{refined.impact_score}/10")
            st.metric("Feasibility", f"{refined.feasibility_score}/10")
            st.metric("Overall", f"{refined.overall_score}/10")
