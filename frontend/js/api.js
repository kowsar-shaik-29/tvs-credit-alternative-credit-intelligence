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
}

// Export singleton and configuration
window.API_CONFIG = API_CONFIG;
window.riskApi = new RiskApiClient();
