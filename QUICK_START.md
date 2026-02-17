# DeepShield AI Assistant - Quick Start Guide

## 🚀 Get Started in 3 Steps

### Step 1: Start the Backend
```bash
cd d:\hackethon\backend
python app.py
```

You should see:
```
✓ Groq AI initialized successfully!
✓ All models initialized successfully!
* Running on http://127.0.0.1:5000
```

### Step 2: Open the Website
Open your browser and go to:
```
http://localhost:5000
```

Or navigate to the HTML files directly:
```
file:///d:/hackethon/deepfake-detection/index.html
```

### Step 3: Click AI Assistant
- Look for **🤖 AI Assistant** in the navigation bar
- Click it to open the chat interface
- Start chatting with Groq AI!

## 💬 Example Questions to Try

1. "What is deepfake detection?"
2. "How does your image analysis work?"
3. "What indicators show a deepfake video?"
4. "How accurate is AI deepfake detection?"
5. "What can I do if I suspect a deepfake?"

## 🎯 Key Features

### Chat Interface
- **Type & Send**: Write messages and press Enter
- **Suggestions**: Click quick-start buttons
- **History**: Your conversation stays visible
- **Export**: Download chat as text file
- **Clear**: Start a new conversation

### Responsive Design
- Works on desktop, tablet, mobile
- Touch-friendly buttons
- Adapts to screen size
- Fast loading

### Smart Responses
- Context-aware answers
- Deepfake expertise
- Multi-turn conversations
- Technical + simple explanations

## 🔗 Integration Points

### From Detection Results
To link from detection pages:
```javascript
// After getting analysis results with ID
window.location.href = `ai-assistant.html?analysis_id=${analysisId}`;
```

### In Your Detection Pages
```html
<button onclick="goToAI()">
  Ask AI Assistant About These Results
</button>

<script>
function goToAI() {
  window.location.href = `ai-assistant.html?analysis_id=${resultId}`;
}
</script>
```

## 🛠️ Configuration

### Environment Variables (.env)
```
GROQ_API_KEY=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
MONGODB_URI=mongodb+srv://sunnyrpatil18_db_user:RRLTWlNKx1LxviYk@...
```

### API Endpoints
- **Chat**: `POST /api/chat`
- **History**: `GET /api/chat/history/<analysis_id>`
- **Export**: `GET /api/chat/export/<analysis_id>`

## 📊 Architecture

```
┌─────────────────────────────────────────┐
│         Frontend (HTML/CSS/JS)          │
│      ai-assistant.html                  │
│      - Chat UI                          │
│      - User messages                    │
│      - Real-time updates                │
└──────────────┬──────────────────────────┘
               │ HTTP/JSON
┌──────────────▼──────────────────────────┐
│         Backend (Flask/Python)          │
│      app.py                             │
│      - /api/chat (POST)                 │
│      - /api/chat/history (GET)          │
│      - /api/chat/export (GET)           │
└──────────────┬──────────────────────────┘
               │ API Call
┌──────────────▼──────────────────────────┐
│         Groq AI (LLM)                   │
│      mixtral-8x7b-32768                 │
│      - Process messages                 │
│      - Generate responses               │
└──────────────┬──────────────────────────┘
               │ Persist
┌──────────────▼──────────────────────────┐
│         MongoDB (Database)              │
│      chat_history collection            │
│      - Store conversations              │
│      - Link to analysis_id              │
└─────────────────────────────────────────┘
```

## 🧪 Test the API

### Using curl
```bash
# Send a message
curl -X POST http://localhost:5000/api/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is deepfake detection?",
    "history": [],
    "analysis_id": "test123"
  }'

# Get chat history
curl http://localhost:5000/api/chat/history/test123

# Export chat
curl http://localhost:5000/api/chat/export/test123 -o chat.txt
```

### Using Python
```python
import requests

# Send message
response = requests.post('http://localhost:5000/api/chat', json={
    'message': 'What is deepfake detection?',
    'history': [],
    'analysis_id': 'test123'
})
print(response.json())

# Get history
history = requests.get('http://localhost:5000/api/chat/history/test123')
print(history.json())
```

## 📱 Mobile Testing

Open on mobile:
```
http://192.168.0.109:5000
```
(Replace IP with your machine's local IP)

The interface will automatically adapt to screen size.

## 🎨 Customization

### Change Theme Color
In `ai-assistant.html`, find:
```css
background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
```
Replace hex colors to customize.

### Modify System Prompt
In `app.py`, find the `/api/chat` function and update:
```python
"content": """You are DeepShield AI Assistant..."""
```

### Add More Suggestions
In `ai-assistant.html`, add to suggestions div:
```html
<div class="suggestion" onclick="sendSuggestion('Your suggestion')">
  Your suggestion text
</div>
```

## ⚙️ Troubleshooting

### Chat not working?
1. Check if backend is running: `http://localhost:5000/api/health`
2. Check browser console for errors (F12 → Console)
3. Check backend logs for messages

### Responses are slow?
- Groq API can take 1-3 seconds
- Check internet connection
- Verify API key is valid

### Messages not saving?
- MongoDB might be down
- Chat still works locally
- Check MongoDB connection in logs

### Export not working?
- Check if chat has messages
- Try different browser
- Check file download location

## 📚 Learn More

- **Groq Docs**: https://console.groq.com/docs
- **Flask Docs**: https://flask.palletsprojects.com
- **MongoDB Docs**: https://docs.mongodb.com

## 🎓 Educational Use

### For Students
- Learn about deepfake detection
- Understand AI conversation systems
- Explore real-time API integration
- Study database persistence

### For Developers
- Groq API integration
- Flask microservices
- Frontend-backend communication
- Real-time updates with WebSocket (future)

## ✅ Validation

Test these scenarios:

1. **Basic Chat**
   - [ ] Send "Hello" → Get response
   - [ ] Message appears immediately
   - [ ] Typing indicator shows
   - [ ] Response appears after 1-3s

2. **Multi-turn**
   - [ ] Send multiple messages
   - [ ] Context is maintained
   - [ ] Each gets response

3. **Export**
   - [ ] Click Export button
   - [ ] File downloads
   - [ ] File has readable content

4. **Navigation**
   - [ ] AI link in all pages
   - [ ] Works from any page
   - [ ] Returns to AI page

5. **Mobile**
   - [ ] Opens on mobile browser
   - [ ] All buttons accessible
   - [ ] Chat scrolls smoothly
   - [ ] Messages readable

## 🚨 Emergency Contacts

If issues persist:
1. Restart backend: `Ctrl+C` then `python app.py`
2. Clear browser cache: `Ctrl+Shift+Delete`
3. Check MongoDB: Run test from `test_database.py`
4. Verify Groq key: Check `.env` file

## 🎉 You're Ready!

Everything is set up and ready to use. Just:
1. Start the backend
2. Open your browser
3. Click AI Assistant
4. Start chatting!

Enjoy exploring DeepShield AI Assistant! 🛡️✨
