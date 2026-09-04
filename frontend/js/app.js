/**
 * TVS Credit NIRNAY - Frontend application controller.
 * Connects 100% dynamically to the FastAPI ML backend.
 */

document.addEventListener("DOMContentLoaded", () => {
  // Elements
  const form = document.getElementById("risk-assessment-form");
  const btnAutofill = document.getElementById("btn-autofill");
  const btnSubmit = document.getElementById("btn-submit");
  const alertBox = document.getElementById("alert-box");
  const backendStatusText = document.getElementById("backend-status-text");
  const statusIndicator = document.querySelector(".status-indicator");

  const resultsPlaceholder = document.getElementById("results-placeholder");
  const resultsLoading = document.getElementById("results-loading");
  const resultsContent = document.getElementById("results-content");

  // Output Fields
  const resProbability = document.getElementById("res-probability");
  const resThreshold = document.getElementById("res-threshold");
  const resRiskClass = document.getElementById("res-risk-class");
  const resPrediction = document.getElementById("res-prediction");
  const resAction = document.getElementById("res-action");

  // Indicators
  const indFss = document.getElementById("ind-fss");
  const indRc = document.getElementById("ind-rc");
  const indEs = document.getElementById("ind-es");
  const indDs = document.getElementById("ind-ds");
  const indLb = document.getElementById("ind-lb");
  const indIb = document.getElementById("ind-ib");
  const indIlr = document.getElementById("ind-ilr");
  const indClb = document.getElementById("ind-clb");
  const factorsList = document.getElementById("factors-list");

  // Update footer links dynamically based on configured backend URL
  const currentBaseUrl = (window.API_CONFIG && window.API_CONFIG.BASE_URL) || "http://localhost:8000";
  const docsLink = document.getElementById("docs-link");
  const healthLink = document.getElementById("health-link");
  if (docsLink) docsLink.href = `${currentBaseUrl}/docs`;
  if (healthLink) healthLink.href = `${currentBaseUrl}/health`;

  // Check Backend Status dynamically
  async function pollBackendHealth() {
    const health = await window.riskApi.checkHealth();
    if (health && health.status === "healthy") {
      backendStatusText.textContent = "Engine Online (Ready)";
      statusIndicator.className = "status-indicator online";
    } else if (health && health.status === "degraded") {
      backendStatusText.textContent = "Engine Degraded (Artifacts Missing)";
      statusIndicator.className = "status-indicator offline";
    } else {
      backendStatusText.textContent = `Backend Offline (${currentBaseUrl})`;
      statusIndicator.className = "status-indicator offline";
    }
  }

  pollBackendHealth();
  setInterval(pollBackendHealth, 10000);

  // Autofill Demo Customer (Verified input yielding 0.416806 default probability)
  btnAutofill.addEventListener("click", () => {
    document.getElementById("age").value = 30;
    document.getElementById("income").value = 50000;
    document.getElementById("loan_amount").value = 40000;
    document.getElementById("credit_score").value = 650;
    document.getElementById("months_employed").value = 36;
    document.getElementById("num_credit_lines").value = 3;
    document.getElementById("interest_rate").value = 10.0;
    document.getElementById("loan_term").value = 36;
    document.getElementById("dti_ratio").value = 0.30;
    document.getElementById("education").value = "Bachelor's";
    document.getElementById("employment_type").value = "Full-time";
    document.getElementById("marital_status").value = "Single";
    document.getElementById("loan_purpose").value = "Other";

    document.getElementById("has_mortgage").checked = false;
    document.getElementById("has_dependents").checked = false;
    document.getElementById("has_cosigner").checked = false;

    showAlert("Loaded demo applicant profile (Age 30, Income 50k, Loan 40k, Purpose: Other)", "success");
  });

  // Handle Form Submission
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    // Extract dynamic form values directly entered by the user
    const payload = {
      age: parseInt(document.getElementById("age").value, 10),
      income: parseFloat(document.getElementById("income").value),
      loan_amount: parseFloat(document.getElementById("loan_amount").value),
      credit_score: parseInt(document.getElementById("credit_score").value, 10),
      months_employed: parseInt(document.getElementById("months_employed").value, 10),
      num_credit_lines: parseInt(document.getElementById("num_credit_lines").value, 10),
      interest_rate: parseFloat(document.getElementById("interest_rate").value),
      loan_term: parseInt(document.getElementById("loan_term").value, 10),
      dti_ratio: parseFloat(document.getElementById("dti_ratio").value),
      education: document.getElementById("education").value,
      employment_type: document.getElementById("employment_type").value,
      marital_status: document.getElementById("marital_status").value,
      has_mortgage: document.getElementById("has_mortgage").checked,
      has_dependents: document.getElementById("has_dependents").checked,
      loan_purpose: document.getElementById("loan_purpose").value,
      has_cosigner: document.getElementById("has_cosigner").checked
    };

    // UI Loading State
    setLoadingState(true);

    try {
      // 1. Call REAL risk assessment endpoint
      const response = await window.riskApi.assessRisk(payload);

      // 2. Call REAL explanation endpoint
      let explanationFactors = [];
      try {
        explanationFactors = await window.riskApi.getExplanation(payload);
      } catch (expErr) {
        console.warn("Explanation endpoint fallback to main response factors:", expErr);
        explanationFactors = response.top_risk_factors || [];
      }

      // 3. Render real backend response
      displayResults(response, explanationFactors);
    } catch (err) {
      showAlert(err.message || "Failed to communicate with TVS Credit Risk Engine.", "danger");
      resultsPlaceholder.classList.remove("hidden");
      resultsContent.classList.add("hidden");
    } finally {
      setLoadingState(false);
    }
  });

  function setLoadingState(loading) {
    if (loading) {
      btnSubmit.disabled = true;
      btnSubmit.textContent = "Processing NIRNAY Evaluation...";
      resultsPlaceholder.classList.add("hidden");
      resultsContent.classList.add("hidden");
      resultsLoading.classList.remove("hidden");
    } else {
      btnSubmit.disabled = false;
      btnSubmit.textContent = "Run NIRNAY Risk Assessment";
      resultsLoading.classList.add("hidden");
    }
  }

  function displayResults(data, explanationFactors) {
    const risk = data.risk_assessment;
    const ind = data.alternative_credit_indicators;
    const factors = (explanationFactors && explanationFactors.length > 0) 
      ? explanationFactors 
      : (data.top_risk_factors || []);

    // Probability & Threshold
    const probPercent = (risk.default_probability * 100).toFixed(2);
    resProbability.textContent = `${probPercent}%`;
    resThreshold.textContent = risk.risk_threshold.toFixed(2);
    resPrediction.textContent = risk.prediction;

    // Risk Classification Badge
    resRiskClass.textContent = risk.risk_classification;
    if (risk.prediction === 1 || risk.risk_classification === "HIGH RISK") {
      resRiskClass.className = "badge badge-lg badge-high-risk";
    } else {
      resRiskClass.className = "badge badge-lg badge-low-risk";
    }

    // Recommended Action Badge
    resAction.textContent = risk.recommended_action;
    if (risk.recommended_action === "ELIGIBLE") {
      resAction.className = "action-badge action-eligible";
    } else if (risk.recommended_action === "MANUAL REVIEW") {
      resAction.className = "action-badge action-review";
    } else {
      resAction.className = "action-badge action-high-risk";
    }

    // Alternative Credit Indicators
    indFss.textContent = ind.financial_stability_score.toFixed(4);
    indRc.textContent = ind.repayment_capacity.toFixed(4);
    indEs.textContent = ind.employment_stability.toFixed(4);
    indDs.textContent = ind.debt_stress.toFixed(4);
    indLb.textContent = ind.loan_burden.toFixed(4);
    indIb.textContent = ind.interest_burden.toFixed(4);
    indIlr.textContent = ind.income_loan_ratio.toFixed(4);
    indClb.textContent = ind.credit_line_burden.toFixed(4);

    // Factors / Model Explainability
    factorsList.innerHTML = "";
    if (factors.length > 0) {
      factors.forEach(f => {
        const item = document.createElement("div");
        item.className = "factor-item";
        const impactClass = f.impact.toLowerCase() === "positive" ? "positive" : "negative";
        item.innerHTML = `
          <span class="factor-name">${escapeHtml(f.feature)}</span>
          <div class="factor-meta">
            <span class="factor-impact ${impactClass}">${escapeHtml(f.impact)}</span>
            <span class="factor-value">${f.value.toFixed(4)}</span>
          </div>
        `;
        factorsList.appendChild(item);
      });
    } else {
      factorsList.innerHTML = `<div class="factor-item"><span class="factor-name">Decision metrics evaluated directly via tree boundaries.</span></div>`;
    }

    // Show Results View
    resultsContent.classList.remove("hidden");
    resultsPlaceholder.classList.add("hidden");
  }

  function showAlert(message, type = "danger") {
    alertBox.textContent = message;
    alertBox.className = `alert-box ${type}`;
    alertBox.classList.remove("hidden");
  }

  function hideAlert() {
    alertBox.classList.add("hidden");
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, 
      tag => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', "'": '&#39;', '"': '&quot;' }[tag] || tag)
    );
  }
});
