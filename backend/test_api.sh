#!/bin/bash
# Deepfake Detection API Testing Script
# Use this script to test the deepfake detection endpoints

BASE_URL="http://localhost:5000"
AUTH_TOKEN="your_jwt_token_here"  # Replace with actual token

echo "================================"
echo "Deepfake Detection API Test Suite"
echo "================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Test 1: Health Check
echo -e "${YELLOW}Test 1: Service Health Check${NC}"
echo "Endpoint: GET /api/deepfake/health"
echo ""
curl -X GET "${BASE_URL}/api/deepfake/health" \
  -H "Content-Type: application/json" \
  -s | jq '.'
echo ""
echo ""

# Test 2: Analyze Image (Anonymous)
echo -e "${YELLOW}Test 2: Analyze Image (No Authentication)${NC}"
echo "Endpoint: POST /api/deepfake/analyze/image"
echo "File: test_image.jpg (replace with your image)"
echo ""
# This requires an actual image file
# curl -X POST "${BASE_URL}/api/deepfake/analyze/image" \
#   -F "file=@test_image.jpg" \
#   -s | jq '.'
echo "Usage:"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/image\" \\"
echo "  -F \"file=@your_image.jpg\""
echo ""
echo ""

# Test 3: Analyze Video (Anonymous)
echo -e "${YELLOW}Test 3: Analyze Video (No Authentication)${NC}"
echo "Endpoint: POST /api/deepfake/analyze/video"
echo "File: test_video.mp4 (replace with your video)"
echo ""
echo "Usage:"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/video\" \\"
echo "  -F \"file=@your_video.mp4\" \\"
echo "  -F \"num_frames=5\""
echo ""
echo ""

# Test 4: Get Detection History (Authenticated)
echo -e "${YELLOW}Test 4: Get Detection History (Requires Authentication)${NC}"
echo "Endpoint: GET /api/deepfake/history"
echo ""
echo "Usage:"
echo "curl -X GET \"${BASE_URL}/api/deepfake/history?limit=20&offset=0\" \\"
echo "  -H \"Authorization: Bearer ${AUTH_TOKEN}\" \\"
echo "  -s | jq '.'"
echo ""
echo "Without token (replace AUTH_TOKEN):"
curl -X GET "${BASE_URL}/api/deepfake/history?limit=5" \
  -H "Content-Type: application/json" \
  -s 2>&1 | head -20
echo ""
echo ""

# Test 5: Get User Statistics (Authenticated)
echo -e "${YELLOW}Test 5: Get User Statistics (Requires Authentication)${NC}"
echo "Endpoint: GET /api/deepfake/stats"
echo ""
echo "Usage:"
echo "curl -X GET \"${BASE_URL}/api/deepfake/stats\" \\"
echo "  -H \"Authorization: Bearer ${AUTH_TOKEN}\" \\"
echo "  -s | jq '.'"
echo ""
echo "Without token (replace AUTH_TOKEN):"
curl -X GET "${BASE_URL}/api/deepfake/stats" \
  -H "Content-Type: application/json" \
  -s 2>&1 | head -20
echo ""
echo ""

# Test 6: Detailed Image Analysis Example
echo -e "${YELLOW}Test 6: Complete Image Analysis Example${NC}"
echo ""
echo "Step 1: Prepare test image"
echo "  Place your test image in uploads/ folder"
echo ""
echo "Step 2: Send request"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/image\" \\"
echo "  -F \"file=@uploads/test.jpg\" \\"
echo "  -H \"Content-Type: multipart/form-data\""
echo ""
echo "Step 3: Response will include:"
echo "  - is_fake: Boolean prediction"
echo "  - fake_confidence: 0-1 score"
echo "  - real_confidence: 0-1 score"
echo "  - recommendation: Human-readable verdict"
echo ""
echo ""

# Test 7: Detailed Video Analysis Example
echo -e "${YELLOW}Test 7: Complete Video Analysis Example${NC}"
echo ""
echo "Step 1: Prepare test video"
echo "  Place your test video in uploads/ folder"
echo ""
echo "Step 2: Send request with frame count"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/video\" \\"
echo "  -F \"file=@uploads/test.mp4\" \\"
echo "  -F \"num_frames=10\" \\"
echo "  -H \"Content-Type: multipart/form-data\""
echo ""
echo "Step 3: Response will include:"
echo "  - frames_analyzed: Number of frames processed"
echo "  - is_fake: Boolean prediction (averaged)"
echo "  - fake_confidence: Average fake score"
echo "  - real_confidence: Average real score"
echo ""
echo ""

# Test 8: Authentication with JWT Token
echo -e "${YELLOW}Test 8: Using Authentication Token${NC}"
echo ""
echo "To get a JWT token, authenticate first:"
echo "curl -X POST \"${BASE_URL}/api/auth/login\" \\"
echo "  -H \"Content-Type: application/json\" \\"
echo "  -d '{\"email\": \"user@example.com\", \"password\": \"password\"}'"
echo ""
echo "Response will include 'token' field"
echo "Use the token in Authorization header:"
echo "curl -X GET \"${BASE_URL}/api/deepfake/history\" \\"
echo "  -H \"Authorization: Bearer YOUR_TOKEN_HERE\""
echo ""
echo ""

# Test 9: Error Handling Examples
echo -e "${YELLOW}Test 9: Error Handling${NC}"
echo ""
echo "Example 1: No file provided"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/image\" \\"
echo "  -H \"Content-Type: multipart/form-data\""
echo "Response: {\"error\": \"No file provided\"}"
echo ""
echo "Example 2: Invalid file type"
echo "curl -X POST \"${BASE_URL}/api/deepfake/analyze/image\" \\"
echo "  -F \"file=@document.pdf\""
echo "Response: {\"error\": \"File type not allowed...\"}"
echo ""
echo "Example 3: File too large (>500MB)"
echo "Response: {\"error\": \"File too large...\"}"
echo ""
echo ""

# Test 10: Batch Processing Example
echo -e "${YELLOW}Test 10: Batch Processing (Multiple Files)${NC}"
echo ""
echo "Process multiple files sequentially:"
echo ""
echo "for file in images/*.jpg; do"
echo "  echo \"Processing: \$file\""
echo "  curl -X POST \"${BASE_URL}/api/deepfake/analyze/image\" \\"
echo "    -F \"file=@\$file\" \\"
echo "    -s | jq '.'"
echo "done"
echo ""
echo ""

# Summary
echo -e "${GREEN}==================================${NC}"
echo -e "${GREEN}API Testing Guide Summary${NC}"
echo -e "${GREEN}==================================${NC}"
echo ""
echo "Available Endpoints:"
echo "  1. GET  /api/deepfake/health                - Check service status"
echo "  2. POST /api/deepfake/analyze/image          - Analyze image file"
echo "  3. POST /api/deepfake/analyze/video          - Analyze video file"
echo "  4. GET  /api/deepfake/history (AUTH)         - Get analysis history"
echo "  5. GET  /api/deepfake/stats (AUTH)           - Get user statistics"
echo ""
echo "Response Codes:"
echo "  200 - Success"
echo "  400 - Bad request (missing file, invalid format)"
echo "  401 - Unauthorized (missing/invalid token)"
echo "  413 - File too large"
echo "  500 - Server error"
echo ""
echo "For more details, see DEEPFAKE_INTEGRATION_README.md"
echo ""
