/**
 * Apex Sports League Hub - Production Runtime Configuration
 *
 * This file allows configuring your API endpoints for production deployment
 * without modifying any core application logic or hardcoding secrets.
 *
 * Instructions:
 * - When deploying to production (Vercel, Netlify, Render):
 *   Set API_BASE to your deployed backend URL, e.g. "https://your-api.onrender.com/api"
 * - If using Vercel or Netlify API rewrites/proxies, set API_BASE to "/api"
 * - If left empty (""), the app will automatically detect:
 *     - Localhost: "http://127.0.0.1:8000/api"
 *     - Production: Relative "/api" with fallback to Standalone Mode
 */
window.__APEX_CONFIG__ = {
  // Production Backend API Base URL (leave empty for automatic detection)
  API_BASE: "",

  // Optional: URL to backend interactive Swagger documentation
  DOCS_URL: ""
};
