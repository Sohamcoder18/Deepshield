// API Configuration
// This file determines the API endpoint for all frontend requests
// Automatically detects the correct backend URL for both local and production environments

const API_CONFIG = {
    // Local development
    DEVELOPMENT: 'http://localhost:5000',
    
    // Get the appropriate API base URL
    getBaseUrl: function() {
        // Check if running on localhost
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return this.DEVELOPMENT;
        }
        // For deployed version, use the same domain (Vercel deployment)
        // The backend is served from the same domain as frontend
        const protocol = window.location.protocol; // http: or https:
        const host = window.location.host; // domain.com
        return protocol + '//' + host;
    },
    
    // Automatically set based on environment
    BASE_URL: (function() {
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {
            return 'http://localhost:5000';
        }
        // Use the same origin for production
        return window.location.origin;
    })()
};

// Convenience function
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + endpoint;
}
