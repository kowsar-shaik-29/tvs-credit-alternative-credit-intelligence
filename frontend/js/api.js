/**
 * Centralized API client for TVS Credit Alternative Credit Intelligence.
 */

const API_CONFIG = {
  get BASE_URL() {
    if (window.APP_CONFIG && typeof window.APP_CONFIG.API_BASE_URL === "string") {
      return window.APP_CONFIG.API_BASE_URL;
    }
    return window.API_BASE_URL || "http://localhost:8000";
  }
};

class RiskApiClient {
  constructor(baseUrl) {
    this._baseUrl = baseUrl;
  }

  get baseUrl() {
    return this._baseUrl || API_CONFIG.BASE_URL;
  }

  async checkHealth() {
    try {
      const response = await fetch(`${this.baseUrl}/health`);
      if (!response.ok) {
        throw new Error(`Health check failed with status ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.warn("Backend health check failed:", error);
      return { status: "offline", model_loaded: false };
    }
  }

  async getModelInfo() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/model-info`);
      if (!response.ok) {
        throw new Error(`Model info error: ${response.status}`);
      }
      return await response.json();
    } catch (error) {
      console.warn("Could not fetch model info:", error);
      return null;
    }
  }

  async assessRisk(applicationData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/risk-assessment`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(applicationData)
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = (data && data.error && data.error.message)
          || (data && data.detail)
          || `Server error (${response.status})`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error("API error during risk assessment:", error);
      throw error;
    }
  }

  async getExplanation(applicationData) {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/risk-assessment/explanation`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "Accept": "application/json"
        },
        body: JSON.stringify(applicationData)
      });

      const data = await response.json();

      if (!response.ok) {
        const errorMsg = (data && data.error && data.error.message)
          || (data && data.detail)
          || `Server error (${response.status})`;
        throw new Error(errorMsg);
      }

      return data;
    } catch (error) {
      console.error("API error during explanation retrieval:", error);
      throw error;
    }
  }

  // NIRNAY Extended APIs

  async getConsentStatus(customerId = "TVS-CUST-10492") {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/consent?customer_id=${encodeURIComponent(customerId)}`);
      if (!response.ok) throw new Error(`Consent fetch failed: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn("Could not fetch consent:", error);
      return null;
    }
  }

  async updateConsent(sourceId, consentGranted, customerId = "TVS-CUST-10492") {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/consent?customer_id=${encodeURIComponent(customerId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ source_id: sourceId, consent_granted: consentGranted })
      });
      if (!response.ok) throw new Error(`Consent update failed: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.error("Error updating consent:", error);
      throw error;
    }
  }

  async runFullNirnayAssessment(applicationData, customerId = "TVS-CUST-10492", archetype = null) {
    try {
      let url = `${this.baseUrl}/api/v1/nirnay/full-assessment?customer_id=${encodeURIComponent(customerId)}`;
      if (archetype && archetype !== "custom") {
        url += `&archetype=${encodeURIComponent(archetype)}`;
      }
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json", "Accept": "application/json" },
        body: JSON.stringify(applicationData)
      });
      const data = await response.json();
      if (!response.ok) {
        throw new Error(data?.detail || `Assessment error (${response.status})`);
      }
      return data;
    } catch (error) {
      console.error("Error during full NIRNAY assessment:", error);
      throw error;
    }
  }

  async runStressTest(applicationData, customerId = "TVS-CUST-10492") {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/stress-test?customer_id=${encodeURIComponent(customerId)}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(applicationData)
      });
      return await response.json();
    } catch (error) {
      console.error("Error in stress test API:", error);
      throw error;
    }
  }

  async listAuditRecords() {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/audit/records`);
      if (!response.ok) throw new Error(`Audit fetch failed: ${response.status}`);
      return await response.json();
    } catch (error) {
      console.warn("Could not fetch audit records:", error);
      return [];
    }
  }

  async askAssistant(question, applicationData, customerId = "TVS-CUST-10492") {
    try {
      const response = await fetch(`${this.baseUrl}/api/v1/assistant/query`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          question: question,
          customer_id: customerId,
          application_data: applicationData
        })
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data?.detail || "Assistant error");
      return data;
    } catch (error) {
      console.error("Assistant API error:", error);
      throw error;
    }
  }
}

// Export singleton and configuration
window.API_CONFIG = API_CONFIG;
window.riskApi = new RiskApiClient();
