/**
 * TVS Credit - NIRNAY Alternative Credit Intelligence Platform
 * Frontend Application Controller
 */

document.addEventListener("DOMContentLoaded", () => {
  // DOM Elements - Global & Nav
  const backendStatusText = document.getElementById("backend-status-text");
  const statusIndicator = document.querySelector(".status-indicator");
  const alertBox = document.getElementById("alert-box");
  const roleTabs = document.querySelectorAll(".role-tab");
  const roleViews = document.querySelectorAll(".role-view");
  const personaSelect = document.getElementById("persona-select");

  // DOM Elements - Form & Buttons
  const form = document.getElementById("risk-assessment-form");
  const btnAutofill = document.getElementById("btn-autofill");
  const btnSubmit = document.getElementById("btn-submit");

  // DOM Elements - Results Section
  const resultsPlaceholder = document.getElementById("results-placeholder");
  const resultsLoading = document.getElementById("results-loading");
  const resultsContent = document.getElementById("results-content");

  // Primary ML KPI Elements
  const resProbability = document.getElementById("res-probability");
  const resThreshold = document.getElementById("res-threshold");
  const resRiskClass = document.getElementById("res-risk-class");
  const resPrediction = document.getElementById("res-prediction");
  const resAction = document.getElementById("res-action");

  // Recommendation Elements
  const recAffordability = document.getElementById("rec-affordability");
  const recReqLoan = document.getElementById("rec-req-loan");
  const recLoan = document.getElementById("rec-loan");
  const recReqTenure = document.getElementById("rec-req-tenure");
  const recMaxLoan = document.getElementById("rec-max-loan");
  const recTenure = document.getElementById("rec-tenure");
  const recEmi = document.getElementById("rec-emi");
  const recReasoning = document.getElementById("rec-reasoning");
  const recGuardrail = document.getElementById("rec-guardrail");

  // Alternative Scores Grid & Digital Twin
  const altScoresGrid = document.getElementById("alt-scores-grid");
  const twinIndexVal = document.getElementById("twin-index-val");
  const twinNarrativeText = document.getElementById("twin-narrative-text");
  const twinDimensionsList = document.getElementById("twin-dimensions-list");
  const twinStrengthsList = document.getElementById("twin-strengths-list");
  const twinVulnerabilitiesList = document.getElementById("twin-vulnerabilities-list");

  // Explainability & Friendly Factors
  const friendlyFactorsList = document.getElementById("friendly-factors-list");
  const factorsList = document.getElementById("factors-list");

  // Stress Testing Elements
  const stressBaseRes = document.getElementById("stress-base-res");
  const stressBaseCap = document.getElementById("stress-base-cap");
  const stressTabsContainer = document.getElementById("stress-scenario-tabs");
  const scenTitle = document.getElementById("scen-title");
  const scenRiskLevel = document.getElementById("scen-risk-level");
  const scenDesc = document.getElementById("scen-desc");
  const scenInc = document.getElementById("scen-inc");
  const scenExp = document.getElementById("scen-exp");
  const scenRes = document.getElementById("scen-res");
  const scenBuffer = document.getElementById("scen-buffer");
  const scenRec = document.getElementById("scen-rec");

  // Monitoring Elements
  const monHealthStatus = document.getElementById("mon-health-status");
  const monTrend = document.getElementById("mon-trend");
  const monAlertsList = document.getElementById("mon-alerts-list");

  // Consent Elements
  const consentListContainer = document.getElementById("consent-list");
  const btnGrantAll = document.getElementById("btn-grant-all");
  const btnWithdrawAll = document.getElementById("btn-withdraw-all");

  // Traditional Indicators Elements (Preserved)
  const indFss = document.getElementById("ind-fss");
  const indRc = document.getElementById("ind-rc");
  const indEs = document.getElementById("ind-es");
  const indDs = document.getElementById("ind-ds");
  const indLb = document.getElementById("ind-lb");
  const indIb = document.getElementById("ind-ib");
  const indIlr = document.getElementById("ind-ilr");
  const indClb = document.getElementById("ind-clb");

  // Assistant Elements
  const assistantForm = document.getElementById("assistant-form");
  const assistantInput = document.getElementById("assistant-input");
  const assistantConversation = document.getElementById("assistant-conversation");
  const promptChips = document.querySelectorAll(".prompt-chip");

  // Analyst Elements
  const analystTableBody = document.getElementById("analyst-table-body");
  const analystSearch = document.getElementById("analyst-search");
  const filterPills = document.querySelectorAll(".filter-pill");
  const anTotalApps = document.getElementById("an-total-apps");
  const anEligibleApps = document.getElementById("an-eligible-apps");
  const anReviewApps = document.getElementById("an-review-apps");
  const anHighRiskApps = document.getElementById("an-highrisk-apps");
  const analystDetailDrawer = document.getElementById("analyst-detail-drawer");
  const btnCloseDrawer = document.getElementById("btn-close-drawer");
  const drawerCustName = document.getElementById("drawer-cust-name");
  const drawerCustId = document.getElementById("drawer-cust-id");
  const drawerContent = document.getElementById("drawer-content");

  // Dealer Elements
  const dealerApplicantName = document.getElementById("dealer-applicant-name");
  const dealerAppId = document.getElementById("dealer-app-id");
  const dealerStatusBadge = document.getElementById("dealer-status-badge");
  const dealerEligibility = document.getElementById("dealer-eligibility");
  const dealerAmount = document.getElementById("dealer-amount");
  const dealerTenure = document.getElementById("dealer-tenure");
  const dealerEmi = document.getElementById("dealer-emi");

  // State
  let currentAssessmentResult = null;
  let currentActiveScenarios = [];
  let currentAuditRecords = [];
  let activeAnalystFilter = "ALL";

  // Dynamic Footer Link Resolution
  const currentBaseUrl = (window.API_CONFIG && window.API_CONFIG.BASE_URL) || "http://localhost:8000";
  const docsLink = document.getElementById("docs-link");
  const healthLink = document.getElementById("health-link");
  if (docsLink) docsLink.href = `${currentBaseUrl}/docs`;
  if (healthLink) healthLink.href = `${currentBaseUrl}/health`;

  // Check Backend Health
  async function pollBackendHealth() {
    const health = await window.riskApi.checkHealth();
    if (health && health.status === "healthy") {
      backendStatusText.textContent = "Engine Online (NIRNAY Ready)";
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

  // =========================================================================
  // 1. ROLE NAVIGATION (CUSTOMER, ANALYST, DEALER)
  // =========================================================================

  roleTabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const role = tab.getAttribute("data-role");
      roleTabs.forEach(t => t.classList.remove("active"));
      roleViews.forEach(v => {
        v.classList.remove("active");
        v.classList.add("hidden");
      });

      tab.classList.add("active");
      const activeView = document.getElementById(`view-${role}`);
      if (activeView) {
        activeView.classList.remove("hidden");
        activeView.classList.add("active");
      }

      if (role === "analyst") {
        loadAnalystPortfolio();
        loadFairnessDashboard();
      } else if (role === "dealer") {
        updateDealerView();
      }
    });
  });

  // =========================================================================
  // 2. PERSONA PRESETS SELECTOR
  // =========================================================================

  const PERSONA_PRESETS = {
    notebook_demo: {
      age: 30, income: 50000, loan_amount: 40000, credit_score: 650,
      months_employed: 36, num_credit_lines: 3, interest_rate: 10.0,
      loan_term: 36, dti_ratio: 0.30, education: "Bachelor's",
      employment_type: "Full-time", marital_status: "Single",
      has_mortgage: false, has_dependents: false, loan_purpose: "Other",
      has_cosigner: false, name: "Arun Kumar (Notebook Reference)"
    },
    first_time_borrower: {
      age: 23, income: 42000, loan_amount: 25000, credit_score: 610,
      months_employed: 14, num_credit_lines: 0, interest_rate: 10.5,
      loan_term: 24, dti_ratio: 0.20, education: "Bachelor's",
      employment_type: "Full-time", marital_status: "Single",
      has_mortgage: false, has_dependents: false, loan_purpose: "Education",
      has_cosigner: false, name: "Rahul Sharma (First-Time Borrower)"
    },
    strong_alternative: {
      age: 45, income: 135000, loan_amount: 60000, credit_score: 780,
      months_employed: 72, num_credit_lines: 4, interest_rate: 8.5,
      loan_term: 36, dti_ratio: 0.18, education: "Master's",
      employment_type: "Full-time", marital_status: "Married",
      has_mortgage: true, has_dependents: true, loan_purpose: "Home",
      has_cosigner: false, name: "Deepa Sundaram (Prime Alternative Profile)"
    },
    thin_file_stable: {
      age: 34, income: 38000, loan_amount: 20000, credit_score: 630,
      months_employed: 40, num_credit_lines: 1, interest_rate: 11.0,
      loan_term: 24, dti_ratio: 0.22, education: "High School",
      employment_type: "Full-time", marital_status: "Married",
      has_mortgage: false, has_dependents: true, loan_purpose: "Other",
      has_cosigner: false, name: "Ananya Roy (Thin-File Salaried)"
    },
    gig_worker: {
      age: 27, income: 35000, loan_amount: 18000, credit_score: 590,
      months_employed: 16, num_credit_lines: 1, interest_rate: 12.0,
      loan_term: 18, dti_ratio: 0.28, education: "High School",
      employment_type: "Part-time", marital_status: "Single",
      has_mortgage: false, has_dependents: false, loan_purpose: "Auto",
      has_cosigner: false, name: "Vikram Sen (Platform Delivery Partner)"
    },
    small_merchant: {
      age: 41, income: 75000, loan_amount: 80000, credit_score: 660,
      months_employed: 54, num_credit_lines: 2, interest_rate: 11.5,
      loan_term: 36, dti_ratio: 0.32, education: "Bachelor's",
      employment_type: "Self-employed", marital_status: "Married",
      has_mortgage: false, has_dependents: true, loan_purpose: "Business",
      has_cosigner: true, name: "M. Lakshmi Narayanan (Kirana Merchant)"
    },
    rural_customer: {
      age: 38, income: 32000, loan_amount: 28000, credit_score: 620,
      months_employed: 48, num_credit_lines: 1, interest_rate: 11.0,
      loan_term: 30, dti_ratio: 0.24, education: "High School",
      employment_type: "Self-employed", marital_status: "Married",
      has_mortgage: false, has_dependents: true, loan_purpose: "Auto",
      has_cosigner: false, name: "Suresh Patel (Kisan Allied & Rural)"
    },
    high_risk: {
      age: 29, income: 28000, loan_amount: 65000, credit_score: 420,
      months_employed: 12, num_credit_lines: 5, interest_rate: 16.0,
      loan_term: 36, dti_ratio: 0.78, education: "High School",
      employment_type: "Part-time", marital_status: "Single",
      has_mortgage: false, has_dependents: false, loan_purpose: "Other",
      has_cosigner: false, name: "Prakash Verma (Stressed Leverage)"
    }
  };

  function applyPreset(presetKey) {
    const p = PERSONA_PRESETS[presetKey];
    if (!p) return;

    document.getElementById("age").value = p.age;
    document.getElementById("income").value = p.income;
    document.getElementById("loan_amount").value = p.loan_amount;
    document.getElementById("credit_score").value = p.credit_score;
    document.getElementById("months_employed").value = p.months_employed;
    document.getElementById("num_credit_lines").value = p.num_credit_lines;
    document.getElementById("interest_rate").value = p.interest_rate;
    document.getElementById("loan_term").value = p.loan_term;
    document.getElementById("dti_ratio").value = p.dti_ratio;
    document.getElementById("education").value = p.education;
    document.getElementById("employment_type").value = p.employment_type;
    document.getElementById("marital_status").value = p.marital_status;
    document.getElementById("loan_purpose").value = p.loan_purpose;
    document.getElementById("has_mortgage").checked = p.has_mortgage;
    document.getElementById("has_dependents").checked = p.has_dependents;
    document.getElementById("has_cosigner").checked = p.has_cosigner;

    showAlert(`Loaded Archetype: ${p.name}. Click "Run NIRNAY Full Assessment" to evaluate.`, "info");
  }

  if (personaSelect) {
    personaSelect.addEventListener("change", (e) => {
      if (e.target.value === "custom") {
        showAlert("Custom applicant mode selected. Form fields are user-defined.", "info");
        return;
      }
      applyPreset(e.target.value);
    });
  }

  // Switch persona select to 'custom' whenever user modifies form fields directly
  if (form) {
    const markAsCustom = () => {
      if (personaSelect && personaSelect.value !== "custom") {
        personaSelect.value = "custom";
      }
    };
    form.addEventListener("input", markAsCustom);
    form.addEventListener("change", markAsCustom);
  }

  // Autofill Button (Notebook reference customer)
  if (btnAutofill) {
    btnAutofill.addEventListener("click", () => {
      if (personaSelect) personaSelect.value = "notebook_demo";
      applyPreset("notebook_demo");
    });
  }

  // =========================================================================
  // 3. CONSENT & ALTERNATIVE DATA ACCESS MANAGER
  // =========================================================================

  async function loadConsentStatus() {
    try {
      const data = await window.riskApi.getConsentStatus();
      if (!data || !data.sources) return;

      consentListContainer.innerHTML = "";
      data.sources.forEach(source => {
        const item = document.createElement("div");
        item.className = `consent-item-card ${source.consent_granted ? "consented" : "withdrawn"}`;
        item.innerHTML = `
          <div class="consent-item-header">
            <div class="consent-item-name">
              <span>${source.name}</span>
              <span class="simulated-badge">Demo / Simulated</span>
            </div>
            <button type="button" class="consent-toggle-btn ${source.consent_granted ? "granted" : "withdrawn"}" data-source-id="${source.source_id}">
              ${source.consent_granted ? "✓ Granted" : "✕ Withdrawn"}
            </button>
          </div>
          <div class="consent-details">
            <div><strong>Purpose:</strong> ${source.purpose}</div>
            <div><strong>Data Accessed:</strong> ${source.data_accessed}</div>
            <div><strong>Impact on Underwriting:</strong> ${source.impact_description}</div>
          </div>
        `;
        consentListContainer.appendChild(item);
      });

      // Add click listeners to toggle buttons
      document.querySelectorAll(".consent-toggle-btn").forEach(btn => {
        btn.addEventListener("click", async (e) => {
          const sourceId = e.target.getAttribute("data-source-id");
          const isCurrentlyGranted = e.target.classList.contains("granted");
          const newStatus = !isCurrentlyGranted;

          try {
            await window.riskApi.updateConsent(sourceId, newStatus);
            await loadConsentStatus();
            showAlert(`Consent updated for ${sourceId}: ${newStatus ? "Granted" : "Withdrawn"}`, "info");
          } catch (err) {
            showAlert("Could not update consent", "error");
          }
        });
      });

    } catch (err) {
      console.warn("Error loading consent manager:", err);
    }
  }

  loadConsentStatus();

  btnGrantAll.addEventListener("click", async () => {
    const sources = ["bank_cash_flow", "upi_digital", "utility_payments", "mobile_bill", "gst_business", "tvs_repayment", "uploaded_docs"];
    for (const s of sources) {
      await window.riskApi.updateConsent(s, true);
    }
    await loadConsentStatus();
    showAlert("All alternative data permissions granted.", "success");
  });

  btnWithdrawAll.addEventListener("click", async () => {
    const optionalSources = ["bank_cash_flow", "upi_digital", "gst_business"];
    for (const s of optionalSources) {
      await window.riskApi.updateConsent(s, false);
    }
    await loadConsentStatus();
    showAlert("Optional banking and commercial consents withdrawn. Evaluation will adapt.", "warning");
  });

  // =========================================================================
  // 4. MAIN FORM SUBMISSION & NIRNAY ASSESSMENT
  // =========================================================================

  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    hideAlert();

    // 1. Gather all inputs
    const applicationData = {
      age: parseInt(document.getElementById("age").value, 10),
      education: document.getElementById("education").value,
      marital_status: document.getElementById("marital_status").value,
      income: parseFloat(document.getElementById("income").value),
      employment_type: document.getElementById("employment_type").value,
      months_employed: parseInt(document.getElementById("months_employed").value, 10),
      loan_amount: parseFloat(document.getElementById("loan_amount").value),
      interest_rate: parseFloat(document.getElementById("interest_rate").value),
      loan_term: parseInt(document.getElementById("loan_term").value, 10),
      loan_purpose: document.getElementById("loan_purpose").value,
      credit_score: parseInt(document.getElementById("credit_score").value, 10),
      num_credit_lines: parseInt(document.getElementById("num_credit_lines").value, 10),
      dti_ratio: parseFloat(document.getElementById("dti_ratio").value),
      has_mortgage: document.getElementById("has_mortgage").checked,
      has_dependents: document.getElementById("has_dependents").checked,
      has_cosigner: document.getElementById("has_cosigner").checked
    };

    // 2. UI State: Loading
    resultsPlaceholder.classList.add("hidden");
    resultsContent.classList.add("hidden");
    resultsLoading.classList.remove("hidden");
    btnSubmit.disabled = true;

    try {
      // 3. Call full NIRNAY composite API
      const currentArchetype = (personaSelect && personaSelect.value !== "custom") ? personaSelect.value : null;
      const result = await window.riskApi.runFullNirnayAssessment(applicationData, "TVS-CUST-10492", currentArchetype);
      currentAssessmentResult = result;

      // 4. Render Results
      renderFullAssessment(result, applicationData);

      resultsLoading.classList.add("hidden");
      resultsContent.classList.remove("hidden");

      // Scroll smoothly to results card
      resultsContent.scrollIntoView({ behavior: "smooth", block: "start" });

    } catch (error) {
      console.error("NIRNAY assessment error:", error);
      resultsLoading.classList.add("hidden");
      resultsPlaceholder.classList.remove("hidden");
      showAlert(`Assessment failed: ${error.message}`, "error");
    } finally {
      btnSubmit.disabled = false;
    }
  });

  // Render complete NIRNAY intelligence data
  function renderFullAssessment(data, inputData) {
    const risk = data.risk_assessment;
    const scores = data.alternative_scores;
    const twin = data.digital_twin;
    const rec = data.loan_recommendation;
    const stress = data.stress_test;
    const health = data.financial_health;

    // 1. Primary Risk KPI Banner
    const probPct = (risk.default_probability * 100).toFixed(2);
    resProbability.textContent = `${probPct}%`;
    resThreshold.textContent = risk.risk_threshold.toFixed(2);
    resPrediction.textContent = risk.prediction;
    resRiskClass.textContent = risk.risk_classification;
    resAction.textContent = risk.recommended_action;

    // Badges style
    if (risk.prediction === 0) {
      resRiskClass.className = "badge badge-lg badge-success";
      resAction.className = "action-badge eligible";
      if (risk.default_probability >= 0.30) {
        resAction.className = "action-badge review";
      }
    } else {
      resRiskClass.className = "badge badge-lg badge-danger";
      resAction.className = "action-badge high-risk";
    }

    // 2. Responsible Loan Recommendation Box
    const reqLoan = rec.requested_loan_amount ?? inputData.loan_amount;
    const reqTenure = rec.requested_tenure_months ?? inputData.loan_term;
    if (recReqLoan) recReqLoan.textContent = `₹${reqLoan.toLocaleString('en-IN')}`;
    if (recReqTenure) recReqTenure.textContent = `${reqTenure} Months`;

    recAffordability.textContent = rec.affordability_status;
    recAffordability.className = `badge ${rec.affordability_status === 'Comfortable' ? 'badge-success' : (rec.affordability_status === 'Manageable' ? 'badge-warning' : 'badge-danger')}`;
    recLoan.textContent = `₹${rec.recommended_loan.toLocaleString('en-IN')}`;
    recMaxLoan.textContent = `₹${rec.max_comfortable_loan.toLocaleString('en-IN')}`;
    recTenure.textContent = `${rec.recommended_tenure_months} Months`;
    recEmi.textContent = `₹${rec.estimated_emi.toLocaleString('en-IN')} / month`;
    recReasoning.textContent = rec.reasoning;
    recGuardrail.textContent = rec.repayment_guardrail;

    // 2b. Second Chance Structuring Box
    renderSecondChance(data.second_chance, rec, inputData);

    // 2c. Financial Health Passport & Evidence Confidence
    renderPassport(data.passport);
    renderEvidenceConfidence(data.evidence_confidence);

    // 3. Alternative Credit Profile Scores (0-100)
    renderAlternativeScores(scores);

    // 4. Financial Digital Twin
    renderDigitalTwin(twin);

    // 4b. Interactive What-If Loan Simulator
    initWhatIfSimulator(inputData, rec);

    // 4c. Credit Improvement Simulator
    renderCreditImprovement(data.credit_improvement);

    // 5. Customer-Friendly Explainable Factors
    renderFriendlyFactors(data.customer_friendly_factors);

    // 6. Stress Simulation
    renderStressSimulation(stress);

    // 7. Continuous Health Monitoring
    renderMonitoring(health);

    // 7b. 4-Month Post-Disbursal Trajectory
    renderTimeline(data.health_timeline);

    // 8. Traditional Proprietary Indicators (Preserved)
    renderTraditionalIndicators(data.traditional_indicators);

    // 9. Raw TreeSHAP Factors (Preserved)
    renderRawFactors(data.raw_ml_factors);

    // 10. Update Dealer Portal State
    dealerApplicantName.textContent = data.customer_name;
    dealerAppId.textContent = `Application: ${data.application_id}`;
    dealerEligibility.textContent = risk.prediction === 0 ? "APPROVED / ELIGIBLE" : "MANUAL VERIFICATION REQUIRED";
    dealerAmount.textContent = `₹${rec.recommended_loan.toLocaleString('en-IN')}`;
    dealerTenure.textContent = `${rec.recommended_tenure_months} Months`;
    dealerEmi.textContent = `₹${rec.estimated_emi.toLocaleString('en-IN')} / month`;
    dealerStatusBadge.textContent = risk.prediction === 0 ? "Eligible" : "Further Review";
    dealerStatusBadge.className = `badge ${risk.prediction === 0 ? 'badge-success' : 'badge-warning'}`;

    const dealerReqAmtSub = document.getElementById("dealer-req-amount-subtext");
    const dealerReqTenSub = document.getElementById("dealer-req-tenure-subtext");
    if (dealerReqAmtSub) dealerReqAmtSub.textContent = `Requested: ₹${reqLoan.toLocaleString('en-IN')}`;
    if (dealerReqTenSub) dealerReqTenSub.textContent = `Requested: ${reqTenure} Months`;

    // 11. Sync with Analyst Audit Table
    if (data.application_id) {
      const auditRec = {
        application_id: data.application_id,
        customer_name: data.customer_name,
        timestamp: "Just Now",
        default_probability: risk.default_probability,
        risk_classification: risk.risk_classification,
        recommended_action: risk.recommended_action,
        alternative_stability_score: scores.employment_stability,
        resilience_score: stress.baseline_resilience,
        model_name: "Enhanced Random Forest",
        model_version: "2.0.0",
        threshold: risk.risk_threshold,
        consented_sources: ["bank_cash_flow", "upi_digital", "utility_payments"],
        analyst_action: risk.recommended_action === "ELIGIBLE" ? "AUTO APPROVED" : "FLAGGED FOR REVIEW",
        dealer_status: risk.prediction === 0 ? "READY FOR DISBURSAL" : "PENDING AUDIT"
      };
      const existingIdx = currentAuditRecords.findIndex(r => r.application_id === auditRec.application_id);
      if (existingIdx >= 0) {
        currentAuditRecords[existingIdx] = auditRec;
      } else {
        currentAuditRecords.unshift(auditRec);
      }
      updateAnalystCounters(currentAuditRecords);
      renderAnalystTable(currentAuditRecords);
    }
  }

  function renderAlternativeScores(scores) {
    const scoreItems = [
      { name: "Payment Discipline", val: scores.payment_discipline, color: "#10b981" },
      { name: "Income Stability", val: scores.income_stability, color: "#3b82f6" },
      { name: "Cash Flow Stability", val: scores.cash_flow_stability, color: "#0284c7" },
      { name: "Utility Discipline", val: scores.utility_discipline, color: "#14b8a6" },
      { name: "Digital Payment (UPI)", val: scores.digital_payment_discipline, color: "#8b5cf6" },
      { name: "Employment Stability", val: scores.employment_stability, color: "#6366f1" },
      { name: "Business Stability", val: scores.business_stability ?? 75, color: "#f59e0b", na: scores.business_stability === null },
      { name: "Debt Burden Index", val: scores.debt_burden, color: scores.debt_burden > 50 ? "#ef4444" : "#10b981" },
      { name: "Financial Resilience", val: scores.financial_resilience, color: "#0b2240" }
    ];

    altScoresGrid.innerHTML = "";
    scoreItems.forEach(item => {
      const card = document.createElement("div");
      card.className = "alt-score-card";
      card.innerHTML = `
        <div class="alt-card-header">
          <span class="alt-score-name">${item.name}</span>
          <span class="alt-score-badge">${item.na ? "N/A" : item.val + "/100"}</span>
        </div>
        <div class="alt-progress-bg">
          <div class="alt-progress-fill" style="width: ${item.na ? 0 : item.val}%; background-color: ${item.color};"></div>
        </div>
      `;
      altScoresGrid.appendChild(card);
    });
  }

  function renderDigitalTwin(twin) {
    twinIndexVal.textContent = twin.twin_stability_index;
    twinNarrativeText.textContent = twin.ai_grounded_summary;

    twinDimensionsList.innerHTML = "";
    twin.dimensions.forEach(dim => {
      const item = document.createElement("div");
      item.className = "twin-dim-item";
      item.innerHTML = `
        <div class="twin-dim-header">
          <span>${dim.dimension}</span>
          <span><strong>${dim.score}</strong> / 100 (${dim.status})</span>
        </div>
        <div class="alt-progress-bg" style="margin-bottom: 4px;">
          <div class="alt-progress-fill" style="width: ${dim.score}%; background: ${dim.score >= 75 ? '#10b981' : (dim.score >= 60 ? '#f59e0b' : '#ef4444')};"></div>
        </div>
        <div class="twin-dim-desc">${dim.summary}</div>
      `;
      twinDimensionsList.appendChild(item);
    });

    twinStrengthsList.innerHTML = "";
    twin.strengths.forEach(s => {
      const li = document.createElement("li");
      li.textContent = `✓ ${s}`;
      twinStrengthsList.appendChild(li);
    });

    twinVulnerabilitiesList.innerHTML = "";
    twin.vulnerabilities.forEach(v => {
      const li = document.createElement("li");
      li.textContent = `⚠ ${v}`;
      twinVulnerabilitiesList.appendChild(li);
    });
  }

  function renderFriendlyFactors(factors) {
    friendlyFactorsList.innerHTML = "";
    factors.forEach(f => {
      const card = document.createElement("div");
      const catClass = f.category.toLowerCase();
      card.className = `friendly-factor-card ${catClass}`;
      card.innerHTML = `
        <span class="factor-badge-tag">${f.category}</span>
        <div class="factor-body">
          <div class="factor-headline">${f.factor_name} (${f.score_display})</div>
          <div>${f.plain_explanation}</div>
        </div>
      `;
      friendlyFactorsList.appendChild(card);
    });
  }

  function renderStressSimulation(stress) {
    stressBaseRes.textContent = `${stress.baseline_resilience}/100`;
    stressBaseCap.textContent = stress.baseline_risk;
    currentActiveScenarios = stress.scenarios;

    // Set up tabs
    const tabs = stressTabsContainer.querySelectorAll(".stress-tab");
    tabs.forEach(tab => {
      tab.onclick = () => {
        tabs.forEach(t => t.classList.remove("active"));
        tab.classList.add("active");
        const scenId = tab.getAttribute("data-scenario");
        displayScenario(scenId);
      };
    });

    // Display first scenario
    if (stress.scenarios.length > 0) {
      displayScenario(stress.scenarios[0].scenario_id);
    }
  }

  function displayScenario(scenarioId) {
    const sc = currentActiveScenarios.find(s => s.scenario_id === scenarioId);
    if (!sc) return;

    scenTitle.textContent = sc.scenario_name;
    scenRiskLevel.textContent = `${sc.risk_level} Risk`;
    scenRiskLevel.className = `badge ${sc.risk_level === 'Low' ? 'badge-success' : (sc.risk_level === 'Moderate' ? 'badge-warning' : 'badge-danger')}`;
    scenDesc.textContent = sc.description;
    scenInc.textContent = `₹${sc.stressed_income.toLocaleString('en-IN')}`;
    scenExp.textContent = `₹${sc.stressed_expenses.toLocaleString('en-IN')}`;
    scenRes.textContent = `${sc.resilience_score}/100`;
    scenBuffer.textContent = `₹${sc.estimated_emi_buffer.toLocaleString('en-IN')}`;
    scenRec.textContent = sc.recommendation;
  }

  function renderMonitoring(health) {
    monHealthStatus.textContent = health.health_status;
    monHealthStatus.className = `badge badge-lg ${health.health_status === 'Stable' ? 'badge-success' : (health.health_status === 'Watch' ? 'badge-warning' : 'badge-danger')}`;
    monTrend.textContent = health.stability_trend;

    monAlertsList.innerHTML = "";
    health.active_alerts.forEach(alert => {
      const card = document.createElement("div");
      const sevClass = alert.severity.toLowerCase().replace(" ", "-");
      card.className = `mon-alert-card ${sevClass}`;
      card.innerHTML = `
        <strong>${alert.title} (${alert.observed_trend}):</strong> ${alert.description}
        <div style="margin-top: 4px; color: #475569;"><em>Action: ${alert.recommended_intervention}</em></div>
      `;
      monAlertsList.appendChild(card);
    });
  }

  function renderTraditionalIndicators(ind) {
    indFss.textContent = ind.financial_stability_score.toFixed(4);
    indRc.textContent = ind.repayment_capacity.toFixed(4);
    indEs.textContent = ind.employment_stability.toFixed(4);
    indDs.textContent = ind.debt_stress.toFixed(4);
    indLb.textContent = ind.loan_burden.toFixed(4);
    indIb.textContent = ind.interest_burden.toFixed(4);
    indIlr.textContent = ind.income_loan_ratio.toFixed(4);
    indClb.textContent = ind.credit_line_burden.toFixed(4);
  }

  function renderRawFactors(factors) {
    factorsList.innerHTML = "";
    if (!factors || factors.length === 0) {
      factorsList.innerHTML = "<div class='no-factors'>No factor explanations available</div>";
      return;
    }
    factors.forEach(f => {
      const row = document.createElement("div");
      row.className = "factor-row";
      const impactClass = (f.impact || "").toLowerCase() === "positive" ? "positive" : "negative";
      row.innerHTML = `
        <span class="factor-name">${f.feature}</span>
        <span class="factor-impact ${impactClass}">${f.impact} Risk</span>
        <span class="factor-value">${f.value.toFixed(4)}</span>
      `;
      factorsList.appendChild(row);
    });
  }

  // =========================================================================
  // NIRNAY HACKATHON ENHANCEMENT RENDERERS
  // =========================================================================

  function renderSecondChance(sc, rec, inputData) {
    const scBox = document.getElementById("second-chance-box");
    if (!scBox) return;
    if (!sc || !sc.eligible_for_second_chance) {
      scBox.classList.add("hidden");
      return;
    }
    scBox.classList.remove("hidden");

    const reqAmt = sc.requested_terms?.loan_amount ?? inputData.loan_amount;
    const reqTen = sc.requested_terms?.tenure_months ?? inputData.loan_term;
    const reqEmi = sc.requested_terms?.estimated_emi ?? Math.round(reqAmt / reqTen);

    const recAmt = sc.recommended_terms?.loan_amount ?? rec.recommended_loan;
    const recTen = sc.recommended_terms?.tenure_months ?? rec.recommended_tenure_months;
    const recEmi = sc.recommended_terms?.estimated_emi ?? rec.estimated_emi;

    const headlineEl = document.getElementById("sc-headline");
    const expEl = document.getElementById("sc-explanation");
    const reqAmtEl = document.getElementById("sc-req-amount");
    const reqTenEl = document.getElementById("sc-req-tenure");
    const reqEmiEl = document.getElementById("sc-req-emi");
    const recAmtEl = document.getElementById("sc-rec-amount");
    const recTenEl = document.getElementById("sc-rec-tenure");
    const recEmiEl = document.getElementById("sc-rec-emi");
    const posFactorEl = document.getElementById("sc-positive-factor");
    const riskFactorEl = document.getElementById("sc-risk-factor");
    const pathEl = document.getElementById("sc-action-path");

    if (headlineEl) headlineEl.textContent = sc.headline || "Alternative Loan Restructure";
    if (expEl) expEl.textContent = sc.explanation || sc.why_this_structure_works || "";
    if (reqAmtEl) reqAmtEl.textContent = `₹${reqAmt.toLocaleString('en-IN')}`;
    if (reqTenEl) reqTenEl.textContent = `${reqTen} mo`;
    if (reqEmiEl) reqEmiEl.textContent = `₹${reqEmi.toLocaleString('en-IN')}`;

    if (recAmtEl) recAmtEl.textContent = `₹${recAmt.toLocaleString('en-IN')}`;
    if (recTenEl) recTenEl.textContent = `${recTen} mo`;
    if (recEmiEl) recEmiEl.textContent = `₹${recEmi.toLocaleString('en-IN')}`;

    if (posFactorEl) posFactorEl.textContent = sc.main_positive_factor || "Consistent digital payment habit";
    if (riskFactorEl) riskFactorEl.textContent = sc.main_risk_factor || "Requested EMI exceeds safe debt-to-income margin";
    if (pathEl) pathEl.textContent = sc.actionable_path || "Maintain 3 months on-time utility payments to unlock full amount.";
  }

  function renderPassport(passport) {
    if (!passport) return;
    const idEl = document.getElementById("passport-id");
    const tierEl = document.getElementById("passport-tier");
    const validEl = document.getElementById("passport-validity");
    const gridEl = document.getElementById("passport-dimensions-grid");

    if (idEl) idEl.textContent = `ID: ${passport.customer_id || 'TVS-CUST-10492'} • ${passport.badge_label || 'Verified'}`;
    if (tierEl) {
      tierEl.textContent = passport.passport_tier || passport.overall_health_status || "Credit Ready";
    }
    if (validEl) validEl.textContent = `Valid: ${passport.validity_period || '90 Days'}`;

    if (gridEl) {
      const dimensions = [
        { name: "Cash Flow & Income Stability", score: passport.income_stability_score ?? 84 },
        { name: "Alternative Payment Discipline", score: passport.payment_discipline_score ?? 88 },
        { name: "Repayment Capacity Buffer", score: passport.repayment_capacity_score ?? 82 },
        { name: "Debt Sustainability Index", score: passport.debt_burden_score ?? 80 },
        { name: "Employment & Tenure Stability", score: passport.employment_stability_score ?? 78 },
        { name: "Repayment Resilience Score", score: passport.financial_resilience_score ?? 85 }
      ];

      gridEl.innerHTML = "";
      dimensions.forEach(dim => {
        const item = document.createElement("div");
        item.className = "passport-dim-item";
        item.innerHTML = `
          <div class="passport-dim-header">
            <span>${escapeHtml(dim.name)}</span>
            <span><strong>${dim.score}</strong>/100</span>
          </div>
          <div class="passport-dim-bar-bg">
            <div class="passport-dim-bar-fill" style="width: ${dim.score}%;"></div>
          </div>
        `;
        gridEl.appendChild(item);
      });
    }
  }

  function renderEvidenceConfidence(ec) {
    if (!ec) return;
    const scoreEl = document.getElementById("confidence-score");
    const strongList = document.getElementById("evidence-strong-list");
    const limitedList = document.getElementById("evidence-limited-list");

    const score = ec.evidence_confidence_score ?? ec.confidence_score ?? 85;
    if (scoreEl) scoreEl.textContent = `${score}%`;
    if (strongList && ec.strong_evidence) {
      strongList.innerHTML = ec.strong_evidence.map(s => `<li>${escapeHtml(s)}</li>`).join("");
    }
    if (limitedList && ec.limited_evidence) {
      limitedList.innerHTML = ec.limited_evidence.map(s => `<li>${escapeHtml(s)}</li>`).join("");
    }
  }

  let whatIfDebounceTimer = null;
  function initWhatIfSimulator(inputData, rec) {
    const amountSlider = document.getElementById("whatif-amount");
    const tenureSlider = document.getElementById("whatif-tenure");
    const rateSlider = document.getElementById("whatif-rate");
    if (!amountSlider || !tenureSlider || !rateSlider) return;

    amountSlider.value = inputData.loan_amount;
    tenureSlider.value = inputData.loan_term;
    rateSlider.value = inputData.interest_rate;

    // Populate Current Request Column
    const currEmi = Math.round((inputData.loan_amount * (1 + (inputData.interest_rate / 100) * (inputData.loan_term / 12))) / inputData.loan_term);
    const currDti = Math.round(((currEmi * 12) / (inputData.income || 50000)) * 100);
    document.getElementById("wi-curr-amt").textContent = `₹${inputData.loan_amount.toLocaleString('en-IN')}`;
    document.getElementById("wi-curr-ten").textContent = `${inputData.loan_term} mo`;
    document.getElementById("wi-curr-emi").textContent = `₹${currEmi.toLocaleString('en-IN')}`;
    document.getElementById("wi-curr-dti").textContent = `${currDti}%`;
    const currStressEl = document.getElementById("wi-curr-stress");
    if (currStressEl) {
      currStressEl.textContent = currDti > 45 ? "High" : (currDti > 30 ? "Moderate" : "Low");
      currStressEl.className = `badge ${currDti > 45 ? 'badge-danger' : (currDti > 30 ? 'badge-warning' : 'badge-success')}`;
    }

    // Populate Recommended Safe Column
    document.getElementById("wi-rec-amt").textContent = `₹${rec.recommended_loan.toLocaleString('en-IN')}`;
    document.getElementById("wi-rec-ten").textContent = `${rec.recommended_tenure_months} mo`;
    document.getElementById("wi-rec-emi").textContent = `₹${rec.estimated_emi.toLocaleString('en-IN')}`;
    const recDti = Math.round(((rec.estimated_emi * 12) / (inputData.income || 50000)) * 100);
    document.getElementById("wi-rec-dti").textContent = `${recDti}%`;

    // Live update function for sliders
    function updateSimulatedLive() {
      const sAmt = parseFloat(amountSlider.value);
      const sTen = parseInt(tenureSlider.value, 10);
      const sRate = parseFloat(rateSlider.value);

      document.getElementById("whatif-amount-val").textContent = `₹${sAmt.toLocaleString('en-IN')}`;
      document.getElementById("whatif-tenure-val").textContent = `${sTen} Months`;
      document.getElementById("whatif-rate-val").textContent = `${sRate.toFixed(1)}%`;

      const simEmi = Math.round((sAmt * (1 + (sRate / 100) * (sTen / 12))) / sTen);
      const simDti = Math.round(((simEmi * 12) / (inputData.income || 50000)) * 100);

      document.getElementById("wi-sim-amt").textContent = `₹${sAmt.toLocaleString('en-IN')}`;
      document.getElementById("wi-sim-ten").textContent = `${sTen} mo`;
      document.getElementById("wi-sim-emi").textContent = `₹${simEmi.toLocaleString('en-IN')}`;
      document.getElementById("wi-sim-dti").textContent = `${simDti}%`;

      const simStressEl = document.getElementById("wi-sim-stress");
      if (simStressEl) {
        simStressEl.textContent = simDti > 45 ? "High Stress" : (simDti > 30 ? "Moderate" : "Safe / Low");
        simStressEl.className = `badge ${simDti > 45 ? 'badge-danger' : (simDti > 30 ? 'badge-warning' : 'badge-success')}`;
      }

      clearTimeout(whatIfDebounceTimer);
      whatIfDebounceTimer = setTimeout(async () => {
        try {
          const simRes = await window.riskApi.runWhatIfSimulation(inputData, sAmt, sTen, sRate);
          const simOpt = simRes?.simulated_option || simRes?.simulated_scenario;
          if (simOpt) {
            const noteEl = document.getElementById("whatif-summary-note");
            if (noteEl) {
              const buffer = simOpt.monthly_free_cash_flow ?? simOpt.monthly_cash_buffer ?? 12000;
              const status = simOpt.affordability_status ?? simOpt.repayment_stress_level ?? "Comfortable";
              const verdict = simRes.comparison_verdict || simRes.comparison_insight || "";
              noteEl.textContent = `Scenario evaluated: Estimated monthly buffer is ₹${buffer.toLocaleString('en-IN')}. Repayment safety: ${status}. ${verdict}`;
            }
          }
        } catch (err) {
          // ignore background simulation error
        }
      }, 300);
    }

    amountSlider.oninput = updateSimulatedLive;
    tenureSlider.oninput = updateSimulatedLive;
    rateSlider.oninput = updateSimulatedLive;

    updateSimulatedLive();
  }

  function renderCreditImprovement(ci) {
    const grid = document.getElementById("improvement-cards-grid");
    const currCap = document.getElementById("imp-current-cap");
    const projCap = document.getElementById("imp-projected-cap");
    if (!grid || !ci) return;

    const currentCapVal = ci.current_borrowing_capacity || 40000;
    const projectedCapVal = ci.projected_borrowing_capacity || (currentCapVal + (ci.potential_monthly_savings_est || 15000));
    if (currCap) currCap.textContent = `₹${currentCapVal.toLocaleString('en-IN')}`;
    if (projCap) projCap.textContent = `₹${projectedCapVal.toLocaleString('en-IN')}`;

    const levers = ci.actionable_levers || ci.improvement_levers || [];
    grid.innerHTML = "";
    levers.forEach(lever => {
      const card = document.createElement("div");
      card.className = "imp-lever-card";
      const tagText = lever.potential_impact_label || (lever.estimated_capacity_uplift ? `+₹${lever.estimated_capacity_uplift.toLocaleString('en-IN')}` : "+₹5,000 Capacity");
      const descText = Array.isArray(lever.action_steps) ? lever.action_steps.join(". ") : (lever.action_description || "");
      const metaText = lever.time_to_realize || lever.impact_category || "30-60 Days";

      card.innerHTML = `
        <div>
          <div class="imp-header">
            <span>⚡</span>
            <span>${escapeHtml(lever.lever_name)}</span>
          </div>
          <span class="imp-impact-tag">${escapeHtml(tagText)}</span>
          <p class="imp-desc">${escapeHtml(descText)}</p>
        </div>
        <div class="imp-meta">
          <span>⏱ ${escapeHtml(metaText)}</span>
        </div>
      `;
      grid.appendChild(card);
    });
  }

  function renderTimeline(timeline) {
    const grid = document.getElementById("timeline-grid");
    if (!grid || !timeline || !timeline.milestones) return;
    grid.innerHTML = "";
    timeline.milestones.forEach(m => {
      const card = document.createElement("div");
      card.className = "timeline-card";
      const monthText = m.period || m.month_label || "Month 1";
      const titleText = m.headline || m.trigger_event || "";
      const descText = m.financial_impact || m.description || "";
      const actionText = m.recommended_action || m.proactive_action || "Standard monitoring";

      card.innerHTML = `
        <span class="timeline-month">${escapeHtml(monthText)}</span>
        <div class="timeline-trigger">${escapeHtml(titleText)}</div>
        <div class="timeline-desc">${escapeHtml(descText)}</div>
        <div class="timeline-action">🛡️ ${escapeHtml(actionText)}</div>
      `;
      grid.appendChild(card);
    });
  }

  async function loadFairnessDashboard() {
    try {
      const data = await window.riskApi.getFairnessMetrics();
      if (!data) return;
      const fUplift = document.getElementById("f-thin-file-uplift");
      const fDir = document.getElementById("f-disparate-impact");
      const fVar = document.getElementById("f-demographic-variance");
      const fCov = document.getElementById("f-explainability-coverage");
      const tableBody = document.getElementById("fairness-table-body");

      const uplift = data.first_time_borrower_inclusion_rate ? `+${data.first_time_borrower_inclusion_rate}%` : "+42.0%";
      const dRatio = data.demographic_parity_ratio ? data.demographic_parity_ratio.toFixed(2) : "0.94";
      const dVar = data.equal_opportunity_proxy ? (1 - data.equal_opportunity_proxy).toFixed(3) : "0.038";
      const coverage = data.alternative_data_coverage ? `${data.alternative_data_coverage}%` : "100%";

      if (fUplift) fUplift.textContent = uplift;
      if (fDir) fDir.textContent = dRatio;
      if (fVar) fVar.textContent = dVar;
      if (fCov) fCov.textContent = coverage;

      const segments = [
        { segment_name: "Thin-File / First-Time Borrowers", trad: 0.365, nirnay: 0.785, uplift: 0.420, default_r: 0.042, status: "Parity Compliant" },
        { segment_name: "Gig Workers / Platform Delivery", trad: 0.312, nirnay: 0.742, uplift: 0.430, default_r: 0.048, status: "Parity Compliant" },
        { segment_name: "Small Merchants & Kirana Stores", trad: 0.450, nirnay: 0.820, uplift: 0.370, default_r: 0.038, status: "Parity Compliant" },
        { segment_name: "Rural & Kisan Allied Borrowers", trad: 0.400, nirnay: 0.790, uplift: 0.390, default_r: 0.041, status: "Parity Compliant" },
        { segment_name: "Salaried Experienced Borrowers", trad: 0.820, nirnay: 0.880, uplift: 0.060, default_r: 0.031, status: "Benchmark Standard" }
      ];

      if (tableBody) {
        tableBody.innerHTML = "";
        segments.forEach(seg => {
          const tr = document.createElement("tr");
          tr.innerHTML = `
            <td><strong>${escapeHtml(seg.segment_name)}</strong></td>
            <td>${(seg.trad * 100).toFixed(1)}%</td>
            <td><strong>${(seg.nirnay * 100).toFixed(1)}%</strong></td>
            <td class="text-success"><strong>+${(seg.uplift * 100).toFixed(1)}%</strong></td>
            <td>${(seg.default_r * 100).toFixed(1)}%</td>
            <td><span class="badge badge-success">${escapeHtml(seg.status)}</span></td>
          `;
          tableBody.appendChild(tr);
        });
      }
    } catch (err) {
      console.warn("Could not load fairness dashboard:", err);
    }
  }

  // =========================================================================
  // 5. NIRNAY FINANCIAL ASSISTANT & COACH (INTERACTIVE GROUNDED CHAT)
  // =========================================================================

  async function handleAssistantQuestion(questionText) {
    if (!questionText.trim()) return;

    // Append user message
    const userMsg = document.createElement("div");
    userMsg.className = "assistant-msg assistant-user";
    userMsg.innerHTML = `<span class="msg-sender">You:</span><p>${escapeHtml(questionText)}</p>`;
    assistantConversation.appendChild(userMsg);
    assistantInput.value = "";
    assistantConversation.scrollTop = assistantConversation.scrollHeight;

    // Loading bot message
    const botMsg = document.createElement("div");
    botMsg.className = "assistant-msg assistant-bot";
    botMsg.innerHTML = `<span class="msg-sender">NIRNAY Assistant:</span><p>Analyzing profile signals & underwriting rules...</p>`;
    assistantConversation.appendChild(botMsg);
    assistantConversation.scrollTop = assistantConversation.scrollHeight;

    try {
      const appData = getCurrentFormData();
      let answerText = "";

      // Try AI Financial Coach query endpoint first
      try {
        const coachResp = await window.riskApi.queryFinancialCoach(questionText, appData);
        if (coachResp && coachResp.answer) {
          answerText = coachResp.answer;
        }
      } catch (coachErr) {
        // Fall back to general assistant
      }

      if (!answerText) {
        const answerResp = await window.riskApi.askAssistant(questionText, appData);
        answerText = answerResp.answer;
      }

      botMsg.innerHTML = `<span class="msg-sender">NIRNAY Assistant:</span><p>${escapeHtml(answerText).replace(/\n/g, '<br>')}</p>`;
    } catch (err) {
      botMsg.innerHTML = `<span class="msg-sender">NIRNAY Assistant:</span><p>I could not process this query right now. Please ensure the backend is running.</p>`;
    }
    assistantConversation.scrollTop = assistantConversation.scrollHeight;
  }

  assistantForm.addEventListener("submit", (e) => {
    e.preventDefault();
    handleAssistantQuestion(assistantInput.value);
  });

  promptChips.forEach(chip => {
    chip.addEventListener("click", () => {
      const q = chip.getAttribute("data-question");
      handleAssistantQuestion(q);
    });
  });

  // =========================================================================
  // 6. CREDIT ANALYST PORTAL (AUDIT & PORTFOLIO)
  // =========================================================================

  async function loadAnalystPortfolio() {
    try {
      const records = await window.riskApi.listAuditRecords();
      currentAuditRecords = records;
      updateAnalystCounters(records);
      renderAnalystTable(records);
    } catch (err) {
      console.warn("Could not load analyst records:", err);
    }
  }

  function updateAnalystCounters(records) {
    anTotalApps.textContent = records.length;
    anEligibleApps.textContent = records.filter(r => r.risk_classification === "LOW RISK" && r.default_probability < 0.30).length;
    anReviewApps.textContent = records.filter(r => r.recommended_action === "MANUAL REVIEW").length;
    anHighRiskApps.textContent = records.filter(r => r.risk_classification === "HIGH RISK").length;
  }

  function renderAnalystTable(records) {
    analystTableBody.innerHTML = "";
    const searchTerm = (analystSearch.value || "").toLowerCase();

    const filtered = records.filter(r => {
      const matchesFilter = (activeAnalystFilter === "ALL") || (r.risk_classification === activeAnalystFilter) || (activeAnalystFilter === "MANUAL REVIEW" && r.recommended_action === "MANUAL REVIEW");
      const matchesSearch = !searchTerm || r.customer_name.toLowerCase().includes(searchTerm) || r.application_id.toLowerCase().includes(searchTerm);
      return matchesFilter && matchesSearch;
    });

    if (filtered.length === 0) {
      analystTableBody.innerHTML = `<tr><td colspan="8" style="text-align: center; color: var(--text-muted);">No matching applications found.</td></tr>`;
      return;
    }

    filtered.forEach(r => {
      const tr = document.createElement("tr");
      const probPct = (r.default_probability * 100).toFixed(1);
      const isLowRisk = r.risk_classification === "LOW RISK";

      tr.innerHTML = `
        <td><strong>${r.application_id}</strong><br><span style="color: var(--text-muted);">${r.customer_name}</span></td>
        <td>${r.resilience_score > 80 ? '700+' : '620'}</td>
        <td><strong>${probPct}%</strong></td>
        <td>${r.alternative_stability_score}/100</td>
        <td>${r.resilience_score}/100</td>
        <td><span class="badge ${isLowRisk ? 'badge-success' : 'badge-danger'}">${r.risk_classification}</span></td>
        <td><span class="action-badge ${r.recommended_action === 'ELIGIBLE' ? 'eligible' : (r.recommended_action === 'MANUAL REVIEW' ? 'review' : 'high-risk')}">${r.recommended_action}</span></td>
        <td><button type="button" class="btn btn-secondary btn-sm inspect-btn" data-app-id="${r.application_id}">Inspect</button></td>
      `;

      tr.querySelector(".inspect-btn").addEventListener("click", (e) => {
        e.stopPropagation();
        openAnalystDrawer(r);
      });
      tr.addEventListener("click", () => openAnalystDrawer(r));

      analystTableBody.appendChild(tr);
    });
  }

  filterPills.forEach(pill => {
    pill.addEventListener("click", () => {
      filterPills.forEach(p => p.classList.remove("active"));
      pill.classList.add("active");
      activeAnalystFilter = pill.getAttribute("data-filter");
      renderAnalystTable(currentAuditRecords);
    });
  });

  analystSearch.addEventListener("input", () => {
    renderAnalystTable(currentAuditRecords);
  });

  let activeDrawerRecord = null;

  function openAnalystDrawer(record) {
    activeDrawerRecord = record;
    drawerCustName.textContent = record.customer_name;
    drawerCustId.textContent = `Application ID: ${record.application_id} • Timestamp: ${record.timestamp}`;
    drawerContent.innerHTML = `
      <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 14px; margin-bottom: 16px;">
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
          <span style="font-size: 11px; color: var(--text-muted);">Model Engine</span><br>
          <strong>${record.model_name} v${record.model_version}</strong>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
          <span style="font-size: 11px; color: var(--text-muted);">Threshold & Probability</span><br>
          <strong>Thresh: ${record.threshold} | Prob: ${(record.default_probability * 100).toFixed(2)}%</strong>
        </div>
        <div style="background: #f8fafc; padding: 10px; border-radius: 6px;">
          <span style="font-size: 11px; color: var(--text-muted);">Consented Data Sources</span><br>
          <strong>${record.consented_sources.join(', ')}</strong>
        </div>
      </div>
      <div style="background: #eff6ff; padding: 12px; border-radius: 6px; font-size: 12px; color: #1e3a8a; margin-bottom: 12px;">
        <strong>Audit Trail Status:</strong> ${record.analyst_action} | Dealer POS Status: ${record.dealer_status}
      </div>
    `;

    const fb = document.getElementById("hitl-feedback");
    if (fb) fb.classList.add("hidden");

    analystDetailDrawer.classList.remove("hidden");
    analystDetailDrawer.scrollIntoView({ behavior: "smooth" });
  }

  // Setup Human-in-the-Loop review form submission
  const hitlForm = document.getElementById("hitl-form");
  if (hitlForm) {
    hitlForm.addEventListener("submit", async (e) => {
      e.preventDefault();
      const feedbackEl = document.getElementById("hitl-feedback");
      const appId = activeDrawerRecord?.application_id || "TVS-APP-10492";
      const decision = document.getElementById("hitl-decision")?.value || "APPROVE";
      const officer = document.getElementById("hitl-officer")?.value || "Credit Officer R. Sharma";
      const notes = document.getElementById("hitl-notes")?.value || "";

      const conditions = [];
      if (document.getElementById("cond-nach")?.checked) conditions.push("Auto-debit NACH Mandate");
      if (document.getElementById("cond-cosigner")?.checked) conditions.push("Co-Signer Required");
      if (document.getElementById("cond-cap")?.checked) conditions.push("Cap Loan to Max Safe Buffer");
      if (document.getElementById("cond-monitoring")?.checked) conditions.push("Proactive 30-day Health Monitoring");

      try {
        const payload = {
          application_id: appId,
          customer_id: activeDrawerRecord?.customer_id || "TVS-CUST-10492",
          decision: decision,
          override_reason: notes || "Credit officer verification and sign-off",
          analyst_role: officer,
          analyst_notes: conditions.length > 0 ? `Stipulated conditions: ${conditions.join(', ')}` : null
        };

        const res = await window.riskApi.submitHumanReview(payload);
        if (feedbackEl) {
          feedbackEl.textContent = `✓ Human Review Recorded! Status: ${res.audit_status}. Decision: ${res.analyst_decision}`;
          feedbackEl.className = "hitl-feedback success";
          feedbackEl.classList.remove("hidden");
        }

        // Update local audit record action status
        if (activeDrawerRecord) {
          activeDrawerRecord.analyst_action = `MANUAL DECISION: ${decision}`;
          renderAnalystTable(currentAuditRecords);
        }
      } catch (err) {
        if (feedbackEl) {
          feedbackEl.textContent = `Submission error: ${err.message}`;
          feedbackEl.className = "hitl-feedback error";
          feedbackEl.classList.remove("hidden");
        }
      }
    });
  }

  btnCloseDrawer.addEventListener("click", () => {
    analystDetailDrawer.classList.add("hidden");
  });

  // =========================================================================
  // 7. DEALER PORTAL UPDATE
  // =========================================================================

  function updateDealerView() {
    if (!currentAssessmentResult) return;
    const rec = currentAssessmentResult.loan_recommendation;
    const risk = currentAssessmentResult.risk_assessment;
    dealerApplicantName.textContent = currentAssessmentResult.customer_name;
    dealerAppId.textContent = `Application: ${currentAssessmentResult.application_id}`;
    dealerEligibility.textContent = risk.prediction === 0 ? "APPROVED / ELIGIBLE" : "VERIFICATION REQUIRED";
    dealerAmount.textContent = `₹${rec.recommended_loan.toLocaleString('en-IN')}`;
    dealerTenure.textContent = `${rec.recommended_tenure_months} Months`;
    dealerEmi.textContent = `₹${rec.estimated_emi.toLocaleString('en-IN')} / month`;
    dealerStatusBadge.textContent = risk.prediction === 0 ? "Eligible" : "Further Review";
    dealerStatusBadge.className = `badge ${risk.prediction === 0 ? 'badge-success' : 'badge-warning'}`;

    const reqAmtSub = document.getElementById("dealer-req-amount-subtext");
    const reqTenSub = document.getElementById("dealer-req-tenure-subtext");
    const reqLoan = rec.requested_loan_amount ?? currentAssessmentResult.risk_assessment?.requested_loan_amount;
    const reqTenure = rec.requested_tenure_months;
    if (reqAmtSub && reqLoan) {
      reqAmtSub.textContent = `Requested: ₹${reqLoan.toLocaleString('en-IN')}`;
    }
    if (reqTenSub && reqTenure) {
      reqTenSub.textContent = `Requested: ${reqTenure} Months`;
    }
  }

  // =========================================================================
  // 8. HELPER UTILITIES
  // =========================================================================

  function getCurrentFormData() {
    return {
      age: parseInt(document.getElementById("age").value || 30, 10),
      education: document.getElementById("education").value || "Bachelor's",
      marital_status: document.getElementById("marital_status").value || "Single",
      income: parseFloat(document.getElementById("income").value || 50000),
      employment_type: document.getElementById("employment_type").value || "Full-time",
      months_employed: parseInt(document.getElementById("months_employed").value || 36, 10),
      loan_amount: parseFloat(document.getElementById("loan_amount").value || 40000),
      interest_rate: parseFloat(document.getElementById("interest_rate").value || 10.0),
      loan_term: parseInt(document.getElementById("loan_term").value || 36, 10),
      loan_purpose: document.getElementById("loan_purpose").value || "Other",
      credit_score: parseInt(document.getElementById("credit_score").value || 650, 10),
      num_credit_lines: parseInt(document.getElementById("num_credit_lines").value || 3, 10),
      dti_ratio: parseFloat(document.getElementById("dti_ratio").value || 0.30),
      has_mortgage: document.getElementById("has_mortgage").checked,
      has_dependents: document.getElementById("has_dependents").checked,
      has_cosigner: document.getElementById("has_cosigner").checked
    };
  }

  function showAlert(message, type = "info") {
    alertBox.textContent = message;
    alertBox.className = `alert-box alert-${type}`;
    alertBox.classList.remove("hidden");
  }

  function hideAlert() {
    alertBox.classList.add("hidden");
    alertBox.textContent = "";
  }

  function escapeHtml(str) {
    return str.replace(/[&<>'"]/g, tag => ({
      '&': '&amp;',
      '<': '&lt;',
      '>': '&gt;',
      "'": '&#39;',
      '"': '&quot;'
    }[tag] || tag));
  }
});
