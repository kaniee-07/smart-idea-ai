"""Plotly visualization functions for SmartIdea AI."""

import plotly.graph_objects as go
from collections import Counter
from typing import List
import math

from src.models import Idea


def impact_vs_feasibility_chart(ideas: List[Idea]) -> go.Figure:
    """Scatter plot of Impact (Y) vs Feasibility (X) for all ideas."""
    titles = [idea.title for idea in ideas]
    categories = [idea.category for idea in ideas]
    feasibility = [idea.feasibility_score for idea in ideas]
    impact = [idea.impact_score for idea in ideas]
    overall = [idea.overall_score for idea in ideas]

    fig = go.Figure()

    fig.add_annotation(x=7.5, y=7.5, text="High Impact<br>High Feasibility",
                       showarrow=False, font=dict(color="#22c55e", size=11), opacity=0.5)
    fig.add_annotation(x=2.5, y=7.5, text="High Impact<br>Low Feasibility",
                       showarrow=False, font=dict(color="#f59e0b", size=11), opacity=0.5)
    fig.add_annotation(x=7.5, y=2.5, text="Low Impact<br>High Feasibility",
                       showarrow=False, font=dict(color="#3b82f6", size=11), opacity=0.5)
    fig.add_annotation(x=2.5, y=2.5, text="Low Impact<br>Low Feasibility",
                       showarrow=False, font=dict(color="#ef4444", size=11), opacity=0.5)

    fig.add_hline(y=5.5, line_dash="dot", line_color="#475569", opacity=0.4)
    fig.add_vline(x=5.5, line_dash="dot", line_color="#475569", opacity=0.4)

    fig.add_trace(go.Scatter(
        x=feasibility,
        y=impact,
        mode="markers+text",
        text=[f"#{i+1}" for i in range(len(ideas))],
        textposition="top center",
        marker=dict(
            size=[o * 4 + 8 for o in overall],
            color=overall,
            colorscale="Viridis",
            showscale=True,
            colorbar=dict(title="Overall Score"),
            line=dict(width=1.5, color="white"),
        ),
        customdata=list(zip(titles, categories, overall)),
        hovertemplate=(
            "<b>%{customdata[0]}</b><br>"
            "Category: %{customdata[1]}<br>"
            "Feasibility: %{x}/10<br>"
            "Impact: %{y}/10<br>"
            "Overall: %{customdata[2]}/10"
            "<extra></extra>"
        ),
    ))

    fig.update_layout(
        title=dict(text="Impact vs Feasibility", font=dict(size=18)),
        xaxis=dict(title="Feasibility Score", range=[0.5, 10.5], tickvals=list(range(1, 11))),
        yaxis=dict(title="Impact Score", range=[0.5, 10.5], tickvals=list(range(1, 11))),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        height=480,
        margin=dict(l=60, r=60, t=60, b=60),
    )

    return fig


def category_distribution_chart(ideas: List[Idea]) -> go.Figure:
    """Bar chart showing idea count per category."""
    category_counts = Counter(idea.category for idea in ideas)
    categories = list(category_counts.keys())
    counts = list(category_counts.values())

    fig = go.Figure(go.Bar(
        x=categories,
        y=counts,
        marker=dict(
            color=counts,
            colorscale="Plasma",
            line=dict(width=0),
        ),
        text=counts,
        textposition="outside",
        hovertemplate="<b>%{x}</b><br>Ideas: %{y}<extra></extra>",
    ))

    fig.update_layout(
        title=dict(text="Ideas by Category", font=dict(size=18)),
        xaxis=dict(title="Category"),
        yaxis=dict(title="Number of Ideas", tickformat="d"),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        height=400,
        margin=dict(l=60, r=40, t=60, b=80),
    )

    return fig


def idea_map_chart(ideas: List[Idea], central_topic: str) -> go.Figure:
    """Simple idea map: Central Topic -> Categories -> Ideas."""
    node_x, node_y, node_text, node_size, node_color = [], [], [], [], []
    edge_x, edge_y = [], []

    # Central node
    node_x.append(0)
    node_y.append(0)
    node_text.append(f"<b>{central_topic[:30]}</b>")
    node_size.append(40)
    node_color.append("#6366f1")

    # Group ideas by category
    category_ideas = {}
    for idea in ideas:
        category_ideas.setdefault(idea.category, []).append(idea)

    categories = list(category_ideas.keys())
    num_categories = len(categories)
    cat_radius = 3.5
    idea_radius = 6.0

    cat_positions = {}
    for i, cat in enumerate(categories):
        angle = (2 * math.pi * i) / num_categories
        cx = cat_radius * math.cos(angle)
        cy = cat_radius * math.sin(angle)
        cat_positions[cat] = (cx, cy)

        node_x.append(cx)
        node_y.append(cy)
        node_text.append(f"<b>{cat}</b>")
        node_size.append(28)
        node_color.append("#8b5cf6")

        edge_x += [0, cx, None]
        edge_y += [0, cy, None]

        cat_ideas = category_ideas[cat]
        num_ideas = len(cat_ideas)

        for j, idea in enumerate(cat_ideas):
            spread = 0.6
            sub_angle = angle + spread * (j - (num_ideas - 1) / 2) * (math.pi / max(num_categories * 2, 1))
            ix = idea_radius * math.cos(sub_angle)
            iy = idea_radius * math.sin(sub_angle)

            node_x.append(ix)
            node_y.append(iy)
            short_title = idea.title[:25] + "..." if len(idea.title) > 25 else idea.title
            node_text.append(short_title)
            node_size.append(18)
            node_color.append("#22d3ee")

            edge_x += [cx, ix, None]
            edge_y += [cy, iy, None]

    fig = go.Figure()

    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(color="#334155", width=1.5),
        hoverinfo="none",
        showlegend=False,
    ))

    fig.add_trace(go.Scatter(
        x=node_x, y=node_y,
        mode="markers+text",
        marker=dict(size=node_size, color=node_color, line=dict(width=1, color="white")),
        text=node_text,
        textposition="top center",
        textfont=dict(size=10, color="#e2e8f0"),
        hoverinfo="text",
        showlegend=False,
    ))

    fig.update_layout(
        title=dict(text="Idea Map", font=dict(size=18)),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        plot_bgcolor="#0f172a",
        paper_bgcolor="#0f172a",
        font=dict(color="#e2e8f0"),
        height=550,
        margin=dict(l=20, r=20, t=60, b=20),
    )

    return fig
