# Deepfake Detection API Testing Script (PowerShell)
# Use this script to test the deepfake detection endpoints on Windows

param(
    [string]$BaseUrl = "http://localhost:5000",
    [string]$Token = "your_jwt_token_here"
)

function Write-Header {
    param([string]$Text)
    Write-Host "`n================================" -ForegroundColor Yellow
    Write-Host $Text -ForegroundColor Yellow
    Write-Host "================================`n" -ForegroundColor Yellow
}

function Write-Test {
    param([string]$Number, [string]$Name)
    Write-Host "Test $Number : $Name" -ForegroundColor Cyan
    Write-Host "=" * 50
}

Write-Host "`n╔═══════════════════════════════════════╗" -ForegroundColor Green
Write-Host "║  Deepfake Detection API Test Suite   ║" -ForegroundColor Green
Write-Host "╚═══════════════════════════════════════╝`n" -ForegroundColor Green

Write-Host "Base URL: $BaseUrl"
Write-Host "Token: $($Token.Substring(0, [Math]::Min(20, $Token.Length)))..."
Write-Host ""

# Test 1: Health Check
Write-Test "1" "Service Health Check"
Write-Host "Endpoint: GET /api/deepfake/health"
Write-Host ""

try {
    $response = Invoke-RestMethod -Uri "$BaseUrl/api/deepfake/health" -Method GET
    $response | ConvertTo-Json | Write-Host
    Write-Host ""
} catch {
    Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
}

# Test 2: Image Analysis Instructions
Write-Test "2" "Analyze Image"
Write-Host "Endpoint: POST /api/deepfake/analyze/image"
Write-Host ""
Write-Host "PowerShell Command:"
Write-Host "$BaseUrl/api/deepfake/analyze/image" -ForegroundColor Gray
Write-Host ""
Write-Host "Example:"
@"
`$ImagePath = "path\to\image.jpg"
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/analyze/image" `
  -Method POST `
  -Form @{ file = Get-Item `$ImagePath }
`$response | ConvertTo-Json
"@ | Write-Host -ForegroundColor Gray
Write-Host ""

# Test 3: Video Analysis Instructions
Write-Test "3" "Analyze Video"
Write-Host "Endpoint: POST /api/deepfake/analyze/video"
Write-Host ""
Write-Host "Example:"
@"
`$VideoPath = "path\to\video.mp4"
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/analyze/video" `
  -Method POST `
  -Form @{
    file = Get-Item `$VideoPath
    num_frames = 5
  }
`$response | ConvertTo-Json
"@ | Write-Host -ForegroundColor Gray
Write-Host ""

# Test 4: Detection History
Write-Test "4" "Get Detection History (Authenticated)"
Write-Host "Endpoint: GET /api/deepfake/history"
Write-Host ""
Write-Host "Example:"
@"
`$headers = @{ Authorization = "Bearer `$Token" }
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/history?limit=20" `
  -Method GET `
  -Headers `$headers
`$response | ConvertTo-Json
"@ | Write-Host -ForegroundColor Gray
Write-Host ""

if ($Token -ne "your_jwt_token_here") {
    try {
        $headers = @{ Authorization = "Bearer $Token" }
        $response = Invoke-RestMethod -Uri "$BaseUrl/api/deepfake/history?limit=5" -Method GET -Headers $headers
        Write-Host "Response (first 5 results):"
        $response | ConvertTo-Json | Write-Host
    } catch {
        Write-Host "Could not retrieve history (invalid token): $($_.Exception.Message)" -ForegroundColor Yellow
    }
}
Write-Host ""

# Test 5: User Statistics
Write-Test "5" "Get User Statistics (Authenticated)"
Write-Host "Endpoint: GET /api/deepfake/stats"
Write-Host ""
Write-Host "Example:"
@"
`$headers = @{ Authorization = "Bearer `$Token" }
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/stats" `
  -Method GET `
  -Headers `$headers
`$response | ConvertTo-Json
"@ | Write-Host -ForegroundColor Gray
Write-Host ""

# Test 6: Complete Image Analysis Example
Write-Test "6" "Complete Image Analysis Example"
Write-Host ""
Write-Host "Step 1: Select image file"
Write-Host "`$ImageFile = Get-Item 'C:\path\to\image.jpg'"
Write-Host ""
Write-Host "Step 2: Send request"
@"
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/analyze/image" `
  -Method POST `
  -Form @{ file = `$ImageFile }
"@ | Write-Host -ForegroundColor Gray
Write-Host ""
Write-Host "Step 3: View results"
Write-Host '$response | Select-Object is_fake, fake_confidence, real_confidence, recommendation | Format-Table' -ForegroundColor Gray
Write-Host ""

# Test 7: Complete Video Analysis Example
Write-Test "7" "Complete Video Analysis Example"
Write-Host ""
Write-Host "Step 1: Select video file"
Write-Host "`$VideoFile = Get-Item 'C:\path\to\video.mp4'"
Write-Host ""
Write-Host "Step 2: Send request with frame count"
@"
`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/deepfake/analyze/video" `
  -Method POST `
  -Form @{
    file = `$VideoFile
    num_frames = 10
  }
"@ | Write-Host -ForegroundColor Gray
Write-Host ""
Write-Host "Step 3: View detailed results"
Write-Host '$response | Format-Table' -ForegroundColor Gray
Write-Host ""

# Test 8: Batch Processing
Write-Test "8" "Batch Processing Multiple Files"
Write-Host ""
Write-Host "Process all images in a folder:"
@"
`$ImageFolder = "C:\path\to\images"
Get-ChildItem `$ImageFolder -Filter "*.jpg" | ForEach-Object {
    Write-Host "Processing: `$(`$_.Name)"
    `$response = Invoke-RestMethod `
      -Uri "$BaseUrl/api/deepfake/analyze/image" `
      -Method POST `
      -Form @{ file = `$_ }
    Write-Host "Result: `$(`$response.is_fake), Confidence: `$(`$response.fake_confidence)"
}
"@ | Write-Host -ForegroundColor Gray
Write-Host ""

# Test 9: Error Handling
Write-Test "9" "Error Handling Examples"
Write-Host ""
Write-Host "Example 1: No file provided"
Write-Host "Response: {`"error`": `"No file provided`"}" -ForegroundColor Gray
Write-Host ""
Write-Host "Example 2: Invalid file type"
Write-Host "Response: {`"error`": `"File type not allowed. Allowed: png, jpg, jpeg, bmp, gif`"}" -ForegroundColor Gray
Write-Host ""
Write-Host "Example 3: File too large (>500MB)"
Write-Host "Response: HTTP 413 - File too large" -ForegroundColor Gray
Write-Host ""

# Test 10: Get JWT Token
Write-Test "10" "Getting Authentication Token"
Write-Host ""
Write-Host "Step 1: Send login request"
@"
`$loginData = @{
    email = "user@example.com"
    password = "your_password"
} | ConvertTo-Json

`$response = Invoke-RestMethod `
  -Uri "$BaseUrl/api/auth/login" `
  -Method POST `
  -ContentType "application/json" `
  -Body `$loginData
"@ | Write-Host -ForegroundColor Gray
Write-Host ""
Write-Host "Step 2: Extract token"
Write-Host '$token = $response.token' -ForegroundColor Gray
Write-Host ""
Write-Host "Step 3: Use token in requests"
Write-Host '$headers = @{ Authorization = "Bearer $token" }' -ForegroundColor Gray
Write-Host ""

# Summary
Write-Header "API Testing Guide Summary"

Write-Host "Available Endpoints:" -ForegroundColor Green
Write-Host "  1. GET  /api/deepfake/health                - Check service status"
Write-Host "  2. POST /api/deepfake/analyze/image          - Analyze image file"
Write-Host "  3. POST /api/deepfake/analyze/video          - Analyze video file"
Write-Host "  4. GET  /api/deepfake/history (AUTH)         - Get analysis history"
Write-Host "  5. GET  /api/deepfake/stats (AUTH)           - Get user statistics"
Write-Host ""

Write-Host "HTTP Response Codes:" -ForegroundColor Green
Write-Host "  200 - Success"
Write-Host "  400 - Bad request (missing file, invalid format)"
Write-Host "  401 - Unauthorized (missing/invalid token)"
Write-Host "  413 - File too large"
Write-Host "  500 - Server error"
Write-Host ""

Write-Host "Response Format:" -ForegroundColor Green
Write-Host "  All responses are JSON"
Write-Host "  Success: {`"success`": true, `"...`": `"...`"}"
Write-Host "  Error: {`"error`": `"error message`"}"
Write-Host ""

Write-Host "For more details, see DEEPFAKE_INTEGRATION_README.md" -ForegroundColor Cyan
Write-Host ""

Write-Host "Testing Guide Complete!" -ForegroundColor Green
