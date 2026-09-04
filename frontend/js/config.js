/**
 * TVS Credit - NIRNAY Frontend Runtime Configuration
 *
 * Configurable API Base URL for local development and production hosting:
 * Priority resolution order:
 * 1. URL query parameter: ?api_url=https://your-cloud-run-backend.a.run.app
 * 2. Window global variable: window.API_BASE_URL
 * 3. LocalStorage override: localStorage.getItem("TVS_API_BASE_URL")
 * 4. Localhost fallback: "http://localhost:8000" (if running locally)
 * 5. Default fallback: "" (relative origin for reverse-proxies or unified domains)
 */

(function () {
  function getQueryParam(param) {
    if (typeof window === "undefined" || !window.location) return null;
    const urlParams = new URLSearchParams(window.location.search);
    return urlParams.get(param);
  }

  function resolveApiBaseUrl() {
    // 1. URL query param
    const queryUrl = getQueryParam("api_url");
    if (queryUrl) {
      return queryUrl.replace(/\/+$/, "");
    }

    // 2. Window global
    if (window.API_BASE_URL) {
      return window.API_BASE_URL.replace(/\/+$/, "");
    }

    // 3. LocalStorage
    try {
      const stored = localStorage.getItem("TVS_API_BASE_URL");
      if (stored) return stored.replace(/\/+$/, "");
    } catch (e) {
      // Ignore storage access errors
    }

    // 4. Localhost / local development fallback
    const isLocalhost =
      window.location.hostname === "localhost" ||
      window.location.hostname === "127.0.0.1" ||
      window.location.protocol === "file:";

    if (isLocalhost) {
      return "http://localhost:8000";
    }

    // 5. Production default: set placeholder or relative root
    // To configure for production, set window.API_BASE_URL or TVS_API_BASE_URL
    return "";
  }

  window.APP_CONFIG = {
    API_BASE_URL: resolveApiBaseUrl(),
    setApiBaseUrl: function (url) {
      if (url) {
        localStorage.setItem("TVS_API_BASE_URL", url.replace(/\/+$/, ""));
      } else {
        localStorage.removeItem("TVS_API_BASE_URL");
      }
      this.API_BASE_URL = resolveApiBaseUrl();
    }
  };
})();
