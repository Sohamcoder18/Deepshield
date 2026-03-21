# URL Scanner - Quick Start Guide

## Setup (Already Done ✓)

The URL scanner has been integrated into `d:\hackethon\backend` with:
- ✓ Google Safe Browsing API key configured
- ✓ Blocklist and allowlist initialized
- ✓ Enhanced detection algorithms active
- ✓ All checks enabled by default

## Basic Usage

### 1. Direct Function Call
```python
from models.scanners.phishing_scanner import scan_url_heuristics

# Scan a URL
result = scan_url_heuristics("https://example.com")

# Result structure
{
    "flagged": False,           # True if malicious/suspicious
    "reasons": ["List of risks"],
    "score": 0.25,              # 0.0-1.0 (higher = more risky)
    "verdict": "safe",          # "malicious", "suspicious", or "safe"
    "checks_run": [...]         # All checks executed
}
```

### 2. HTTP API (Flask)
```bash
POST /api/scan/url
Content-Type: application/json

{
    "url": "https://suspicious-domain.xyz"
}
```

**Response:**
```json
{
    "status": "success",
    "analysis_type": "url",
    "url": "https://suspicious-domain.xyz",
    "risk_score": 0.95,
    "is_fake": true,
    "reasons": [
        "Suspicious TLD: .xyz",
        "Suspicious keyword 'secure' in URL",
        "Suspicious keyword 'verify' in URL"
    ],
    "verdict": "malicious",
    "recommendation": "This URL appears malicious. Avoid clicking.",
    "timestamp": "2024-01-01T12:00:00"
}
```

## Understanding Verdicts

### MALICIOUS (Score >= 0.70)
- **Meaning:** High confidence the URL is malicious
- **Examples:** Blocklisted domains, multiple risk signals
- **Action:** Block/warn user immediately

### SUSPICIOUS (Score 0.40-0.69)
- **Meaning:** Moderate risk detected
- **Examples:** Shorteners, single risk signal
- **Action:** Warn user to be cautious

### SAFE (Score < 0.40)
- **Meaning:** No significant risks detected
- **Examples:** Known legitimate domains
- **Action:** Allow normal access

## Managing Blocklist

### Add Malicious Domain
Edit `d:\hackethon\backend\data\url_list.json`:
```json
{
  "blocklist": [
    "existing-malicious.xyz",
    "new-malicious-domain.tk"  // Add here
  ],
  "allowlist": [...]
}
```

### Add Trusted Domain
Edit `d:\hackethon\backend\data\url_list.json`:
```json
{
  "blocklist": [...],
  "allowlist": [
    "existing-trusted.com",
    "new-trusted-domain.com"  // Add here
  ]
}
```

Changes take effect immediately on next URL scan.

## Test the Scanner

Run the test suite:
```bash
cd d:\hackethon\backend
python test_url_scanner_improved.py
```

Expected output: **13 passed, 0 failed**

## Common Phishing Patterns Detected

1. **Suspicious Keywords:**
   - secure, verify, login, pay, payments, upi, confirm, account, auth, password, reset, update, urgent, action-required, click-here, validate, authenticate, suspended, locked, compromised, breach, fraud, alert

2. **Risky TLDs:**
   - .xyz, .top, .club, .info, .online, .site, .icu, .pw, .ml, .tk, .ga, .cf, .gq

3. **Obfuscation Techniques:**
   - Raw IP addresses (192.168.1.1)
   - URL shorteners (bit.ly, tinyurl.com, t.co, etc.)
   - Punycode/IDN spoofing (xn--)
   - Excessive hyphens (>3)
   - Very long URLs (>150 chars)

4. **Insecure Protocols:**
   - HTTP instead of HTTPS (especially for payment/banking)

## Debug Mode

To see detailed analysis:
```python
result = scan_url_heuristics("https://suspicious-url.xyz")

print(f"Score: {result['score']}")
print(f"Verdict: {result['verdict']}")
print(f"Checks: {result['checks_run']}")
for reason in result['reasons']:
    print(f"  - {reason}")
```

## Performance Tips

1. **Caching:** Blocklist is loaded once; subsequent calls are fast
2. **Timeouts:** Google Safe Browsing has 3-second timeout
3. **Batch Processing:** Can process many URLs in parallel
4. **Rate Limiting:** 10,000 Google Safe Browsing queries/day

## Configuration

Edit `d:\hackethon\backend\.env`:
```bash
# Disable specific checks if needed
ENABLE_GOOGLE_SAFE_BROWSING=true   # Google Safe Browsing API
ENABLE_DOMAIN_AGE_CHECK=true       # WHOIS domain age check
ENABLE_SSL_CHECK=true               # SSL certificate validation
ENABLE_PAGE_INSPECTION=true         # Page content analysis

# API Key (change if needed)
GOOGLE_SAFE_BROWSING_API_KEY=AIzaSyCb9e6CeitMGLCooN0TC08E3_rceF2efpQ
```

## Troubleshooting

### Issue: "No clear issues detected" for known malicious URL
**Solution:** Add domain to blocklist in `url_list.json`

### Issue: Google Safe Browsing returns 400 error
**Solution:** Invalid URL format. Ensure URL starts with http:// or https://

### Issue: Slow scanning
**Solution:** 
- Google Safe Browsing timeout (adjust if needed)
- Check network connectivity
- Ensure SSL/TLS certificates can be validated

### Issue: Too many false positives
**Solution:**
- Add domain to allowlist in `url_list.json`
- Review scoring weights in phishing_scanner.py

## Integration Example

### Flask/FastAPI Integration
```python
from flask import Flask, request, jsonify
from models.scanners.phishing_scanner import scan_url_heuristics

@app.route('/api/scan/url', methods=['POST'])
def scan_url():
    data = request.get_json()
    url = data.get('url')
    
    result = scan_url_heuristics(url)
    
    return jsonify({
        'risk_score': result['score'],
        'is_malicious': result['flagged'],
        'verdict': result['verdict'],
        'reasons': result['reasons']
    })
```

## Support Files

- **Main Scanner:** `d:\hackethon\backend\models\scanners\phishing_scanner.py`
- **Config:** `d:\hackethon\backend\.env`
- **Blocklist:** `d:\hackethon\backend\data\url_list.json`
- **Tests:** `d:\hackethon\backend\test_url_scanner_improved.py`
- **Docs:** `d:\hackethon\backend\URL_SCANNER_IMPROVEMENTS.md` (this file)

## Status
✅ **Production Ready**
- All tests Pass
- Google Safe Browsing API integrated
- Blocklist/allowlist functional
- Enhanced detection active
