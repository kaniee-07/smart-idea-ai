// SmartIdea AI - Frontend Client Application
let currentResult = null;
let currentImageBase64 = null;

// DOM Elements
const promptInput = document.getElementById("promptInput");
const domainSelect = document.getElementById("domainSelect");
const constraintsInput = document.getElementById("constraintsInput");
const numIdeasSelect = document.getElementById("numIdeasSelect");
const imageInput = document.getElementById("imageInput");
const dropzone = document.getElementById("dropzone");
const dropzoneLabel = document.getElementById("dropzoneLabel");
const imagePreviewContainer = document.getElementById("imagePreviewContainer");
const imagePreview = document.getElementById("imagePreview");
const removeImgBtn = document.getElementById("removeImgBtn");
const generateBtn = document.getElementById("generateBtn");
const apiStatusBar = document.getElementById("apiStatusBar");
const apiStatusText = document.getElementById("apiStatusText");
const statusDot = apiStatusBar.querySelector(".status-dot");
const alertBox = document.getElementById("alertBox");
const alertMessage = document.getElementById("alertMessage");
const alertCloseBtn = document.getElementById("alertCloseBtn");
const welcomeState = document.getElementById("welcomeState");
const loadingState = document.getElementById("loadingState");
const resultsContainer = document.getElementById("resultsContainer");
const detectedDomainBadge = document.getElementById("detectedDomainBadge");
const problemSummaryText = document.getElementById("problemSummaryText");
const opportunitiesContainer = document.getElementById("opportunitiesContainer");
const recTitle = document.getElementById("recTitle");
const recCategory = document.getElementById("recCategory");
const recReason = document.getElementById("recReason");
const recImpact = document.getElementById("recImpact");
const recFeasibility = document.getElementById("recFeasibility");
const recOverall = document.getElementById("recOverall");
const ideasList = document.getElementById("ideasList");
const generatedIdeasHeading = document.getElementById("generatedIdeasHeading");
const refineSelect = document.getElementById("refineSelect");
const refineInput = document.getElementById("refineInput");
const refineBtn = document.getElementById("refineBtn");
const refineResultContainer = document.getElementById("refineResultContainer");

// Check Health on Page Load
async function checkHealth() {
  try {
    const res = await fetch("/api/health");
    if (res.ok) {
      const data = await res.json();
      if (data.api_key_configured) {
        statusDot.className = "status-dot active";
        apiStatusText.textContent = "Gemini API Connected";
      } else {
        statusDot.className = "status-dot error";
        apiStatusText.textContent = "API key missing in .env / Vercel";
      }
    } else {
      statusDot.className = "status-dot error";
      apiStatusText.textContent = "API unavailable";
    }
  } catch (err) {
    statusDot.className = "status-dot error";
    apiStatusText.textContent = "Offline or connecting...";
  }
}
checkHealth();

// Alert helper
function showAlert(msg) {
  alertMessage.textContent = msg;
  alertBox.style.display = "flex";
  alertBox.scrollIntoView({ behavior: "smooth", block: "center" });
}

function hideAlert() {
  alertBox.style.display = "none";
}

alertCloseBtn.addEventListener("click", hideAlert);

// Image handling
imageInput.addEventListener("change", handleImageSelect);
dropzone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropzone.style.borderColor = "#6366f1";
});
dropzone.addEventListener("dragleave", () => {
  dropzone.style.borderColor = "";
});
dropzone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropzone.style.borderColor = "";
  if (e.dataTransfer.files && e.dataTransfer.files[0]) {
    handleFile(e.dataTransfer.files[0]);
  }
});

function handleImageSelect(e) {
  if (e.target.files && e.target.files[0]) {
    handleFile(e.target.files[0]);
  }
}

function handleFile(file) {
  if (!file.type.match(/image\/(png|jpeg|jpg)/)) {
    showAlert("Please upload a PNG, JPG, or JPEG image.");
    return;
  }
  const reader = new FileReader();
  reader.onload = (event) => {
    currentImageBase64 = event.target.result;
    imagePreview.src = currentImageBase64;
    dropzoneLabel.style.display = "none";
    imagePreviewContainer.style.display = "flex";
  };
  reader.readAsDataURL(file);
}

removeImgBtn.addEventListener("click", (e) => {
  e.stopPropagation();
  currentImageBase64 = null;
  imageInput.value = "";
  imagePreview.src = "";
  imagePreviewContainer.style.display = "none";
  dropzoneLabel.style.display = "flex";
});

// Quick chips auto-fill
document.querySelectorAll(".chip").forEach((chip) => {
  chip.addEventListener("click", () => {
    refineInput.value = chip.textContent;
    refineInput.focus();
  });
});

// Generate Ideas handler
generateBtn.addEventListener("click", async () => {
  const prompt = promptInput.value.trim();
  if (!prompt) {
    showAlert("Please enter an Idea / Problem prompt before generating.");
    promptInput.focus();
    return;
  }

  hideAlert();
  setGenerating(true);

  const payload = {
    prompt: prompt,
    domain: domainSelect.value,
    constraints: constraintsInput.value.trim(),
    number_of_ideas: parseInt(numIdeasSelect.value, 10),
    image_base64: currentImageBase64,
  };

  try {
    const res = await fetch("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || data.error || "Generation failed.");
    }

    currentResult = data.data;
    renderResults(data.data, data.charts);
  } catch (err) {
    showAlert(err.message || "An unexpected error occurred. Please check your Gemini API key.");
  } finally {
    setGenerating(false);
  }
});

function setGenerating(isLoading) {
  generateBtn.disabled = isLoading;
  const btnText = generateBtn.querySelector(".btn-text");
  const spinner = generateBtn.querySelector(".spinner");

  if (isLoading) {
    btnText.textContent = "Generating...";
    spinner.style.display = "inline-block";
    welcomeState.style.display = "none";
    resultsContainer.style.display = "none";
    loadingState.style.display = "flex";
  } else {
    btnText.textContent = "Generate Ideas";
    spinner.style.display = "none";
    loadingState.style.display = "none";
  }
}

// Render Results
function renderResults(result, charts) {
  resultsContainer.style.display = "block";
  resultsContainer.scrollIntoView({ behavior: "smooth" });

  // 1. Innovation Report
  detectedDomainBadge.textContent = result.detected_domain;
  problemSummaryText.textContent = result.problem_summary;

  opportunitiesContainer.innerHTML = "";
  (result.trends_or_opportunities || []).forEach((opp) => {
    const span = document.createElement("span");
    span.className = "badge badge-opportunity";
    span.textContent = opp;
    opportunitiesContainer.appendChild(span);
  });

  // 2. Recommended Idea
  const ideas = result.ideas || [];
  const recommended = ideas.find((i) => i.title === result.recommended_idea) || ideas[0] || {};

  recTitle.textContent = recommended.title || "Top Idea";
  recCategory.textContent = recommended.category || "";
  recReason.textContent = result.recommendation_reason || "Strongest impact and feasibility balance.";
  recImpact.textContent = `${recommended.impact_score || 0}/10`;
  recFeasibility.textContent = `${recommended.feasibility_score || 0}/10`;
  const overall = ((recommended.impact_score + recommended.feasibility_score) / 2).toFixed(1);
  recOverall.textContent = `${overall}/10`;

  // 3. Ideas Accordion List
  generatedIdeasHeading.textContent = `Generated Ideas (${ideas.length})`;
  ideasList.innerHTML = "";
  refineSelect.innerHTML = "";

  ideas.forEach((idea, idx) => {
    const isRec = idea.title === result.recommended_idea;
    const ideaOverall = ((idea.impact_score + idea.feasibility_score) / 2).toFixed(1);

    // Option for refinement selectbox
    const opt = document.createElement("option");
    opt.value = idea.title;
    opt.textContent = `${idx + 1}. ${idea.title}`;
    refineSelect.appendChild(opt);

    // Accordion item
    const item = document.createElement("div");
    item.className = `idea-accordion ${isRec ? "recommended" : ""}`;

    const header = document.createElement("div");
    header.className = "accordion-header";
    header.innerHTML = `
      <div class="accordion-title-wrap">
        <span class="badge badge-purple">${escapeHtml(idea.category)}</span>
        <span class="accordion-title">Idea #${idx + 1} - ${escapeHtml(idea.title)} ${isRec ? "⭐" : ""}</span>
      </div>
      <div class="accordion-toggle">Score: ${ideaOverall}/10 ▾</div>
    `;

    const body = document.createElement("div");
    body.className = `accordion-body ${idx === 0 ? "open" : ""}`;

    const stepsHtml = (idea.implementation_steps || [])
      .map((step) => `<li>${escapeHtml(step)}</li>`)
      .join("");

    body.innerHTML = `
      <div class="field-group">
        <div class="field-label">Problem:</div>
        <p class="field-value">${escapeHtml(idea.problem)}</p>
      </div>
      <div class="field-group">
        <div class="field-label">Solution:</div>
        <p class="field-value">${escapeHtml(idea.solution)}</p>
      </div>
      <div class="field-group">
        <div class="field-label">Target Users:</div>
        <p class="field-value">${escapeHtml(idea.target_users)}</p>
      </div>
      <div class="field-group">
        <div class="field-label">What Makes It Innovative:</div>
        <p class="field-value">${escapeHtml(idea.innovation)}</p>
      </div>
      <div class="field-group">
        <div class="field-label">Why It Matters:</div>
        <p class="field-value">${escapeHtml(idea.why_it_matters)}</p>
      </div>
      <div class="metrics-grid">
        <div class="metric-box">
          <span class="metric-label">Impact</span>
          <span class="metric-value">${idea.impact_score}/10</span>
        </div>
        <div class="metric-box">
          <span class="metric-label">Feasibility</span>
          <span class="metric-value">${idea.feasibility_score}/10</span>
        </div>
        <div class="metric-box highlight">
          <span class="metric-label">Overall</span>
          <span class="metric-value">${ideaOverall}/10</span>
        </div>
      </div>
      <div class="field-group">
        <div class="field-label">Implementation Steps:</div>
        <ol class="steps-list">${stepsHtml}</ol>
      </div>
    `;

    header.addEventListener("click", () => {
      const isOpen = body.classList.contains("open");
      body.classList.toggle("open", !isOpen);
      header.querySelector(".accordion-toggle").textContent = `Score: ${ideaOverall}/10 ${isOpen ? "▾" : "▴"}`;
    });

    item.appendChild(header);
    item.appendChild(body);
    ideasList.appendChild(item);
  });

  // 4. Render Plotly Charts
  if (charts && window.Plotly) {
    try {
      if (charts.scatter) {
        Plotly.newPlot("scatterChart", charts.scatter.data, charts.scatter.layout, { responsive: true, displayModeBar: false });
      }
      if (charts.category) {
        Plotly.newPlot("categoryChart", charts.category.data, charts.category.layout, { responsive: true, displayModeBar: false });
      }
      if (charts.map) {
        Plotly.newPlot("mapChart", charts.map.data, charts.map.layout, { responsive: true, displayModeBar: false });
      }
    } catch (chartErr) {
      console.error("Plotly render error:", chartErr);
    }
  }

  // Reset refinement card
  refineResultContainer.style.display = "none";
}

// Refine Idea handler
refineBtn.addEventListener("click", async () => {
  if (!currentResult || !currentResult.ideas) {
    showAlert("Please generate ideas before attempting refinement.");
    return;
  }

  const selectedTitle = refineSelect.value;
  const instruction = refineInput.value.trim();

  if (!instruction) {
    showAlert("Please enter an instruction describing how to refine the idea.");
    refineInput.focus();
    return;
  }

  const selectedIdea = currentResult.ideas.find((i) => i.title === selectedTitle);
  if (!selectedIdea) {
    showAlert("Selected idea not found.");
    return;
  }

  hideAlert();
  setRefining(true);

  try {
    const res = await fetch("/api/refine", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({
        idea: selectedIdea,
        refinement_instruction: instruction,
      }),
    });

    const data = await res.json();
    if (!res.ok || !data.success) {
      throw new Error(data.detail || data.error || "Refinement failed.");
    }

    renderRefinedIdea(data.data);
  } catch (err) {
    showAlert(err.message || "Refinement failed. Please try again.");
  } finally {
    setRefining(false);
  }
});

function setRefining(isLoading) {
  refineBtn.disabled = isLoading;
  const btnText = refineBtn.querySelector(".btn-text");
  const spinner = refineBtn.querySelector(".spinner");

  if (isLoading) {
    btnText.textContent = "Refining...";
    spinner.style.display = "inline-block";
  } else {
    btnText.textContent = "Refine Idea";
    spinner.style.display = "none";
  }
}

function renderRefinedIdea(refined) {
  refineResultContainer.style.display = "block";
  refineResultContainer.scrollIntoView({ behavior: "smooth" });

  document.getElementById("refinedTitle").textContent = refined.title;
  document.getElementById("refinedCategory").textContent = refined.category;
  document.getElementById("refinedProblem").textContent = refined.problem;
  document.getElementById("refinedSolution").textContent = refined.solution;
  document.getElementById("refinedTargetUsers").textContent = refined.target_users;
  document.getElementById("refinedInnovation").textContent = refined.innovation;
  document.getElementById("refinedWhyItMatters").textContent = refined.why_it_matters;
  document.getElementById("refinedImpact").textContent = `${refined.impact_score}/10`;
  document.getElementById("refinedFeasibility").textContent = `${refined.feasibility_score}/10`;

  const overall = ((refined.impact_score + refined.feasibility_score) / 2).toFixed(1);
  document.getElementById("refinedOverall").textContent = `${overall}/10`;

  const stepsList = document.getElementById("refinedStepsList");
  stepsList.innerHTML = (refined.implementation_steps || [])
    .map((s) => `<li>${escapeHtml(s)}</li>`)
    .join("");
}

function escapeHtml(str) {
  if (!str) return "";
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
