// API Configuration
// Uses port 8080 to avoid conflict with http.server on port 5000

const API_CONFIG = {
    // Local development - port 5001 for Flask backend
    DEVELOPMENT: 'http://localhost:5001',
    
    // Get the appropriate API base URL
    getBaseUrl: function() {
        return this.DEVELOPMENT;
    },
    
    // Automatically set based on environment
    BASE_URL: (function() {
        var hostname = window.location.hostname;
        if (hostname === 'localhost' || hostname === '127.0.0.1' || 
            hostname === '[::1]' || hostname === '[::]' || hostname === '') {
            return 'http://localhost:5001';
        }
        return window.location.origin;
    })()
};

// Convenience function
function getApiUrl(endpoint) {
    return API_CONFIG.BASE_URL + endpoint;
}
