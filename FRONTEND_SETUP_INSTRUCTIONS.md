# 🎨 Frontend Setup Instructions

## 📦 Required Dependencies Installation

To complete the frontend integration, you need to install the react-markdown package for rendering formatted AI responses.

### Step 1: Navigate to Frontend Directory

```bash
cd Data_Analysis_Project/frontend
```

### Step 2: Install Required Packages

```bash
npm install react-markdown remark-gfm
```

**Packages:**
- `react-markdown` - For rendering markdown in chat messages
- `remark-gfm` - GitHub Flavored Markdown support (tables, strikethrough, etc.)

### Step 3: Verify Installation

Check that the packages are added to `package.json`:

```json
{
  "dependencies": {
    "react-markdown": "^9.0.0",
    "remark-gfm": "^4.0.0"
  }
}
```

---

## 🔧 Environment Configuration

### Create `.env.local` file in frontend directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: For production
# NEXT_PUBLIC_API_URL=https://your-production-api.com
```

---

## 🚀 Running the Frontend

### Development Mode:

```bash
npm run dev
```

The frontend will be available at: `http://localhost:3000`

### Production Build:

```bash
npm run build
npm start
```

---

## ✅ ChatWidget Features

The enhanced ChatWidget now includes:

### 1. **Streaming Support**
- Real-time message display as AI generates response
- Toggle streaming on/off with checkbox
- Stop button to cancel streaming

### 2. **Chat History**
- Automatically loads last 20 messages on open
- Persists across sessions
- Clear history button

### 3. **Markdown Rendering**
- Formatted text with bold, italic, lists
- Code blocks with syntax highlighting
- Tables and links support

### 4. **Enhanced UI**
- Beautiful gradient header
- Smooth animations
- Loading indicators
- Source citations display
- RTL support for Arabic

### 5. **Error Handling**
- Connection error messages
- Retry functionality
- Graceful degradation

---

## 🎯 Usage Examples

### Example 1: Medical Question in Arabic

```
User: ما هو أفضل مضاد حيوي لعلاج E. coli؟

Bot: بناءً على بيانات المستشفى الحالية:

**المضادات الحيوية الموصى بها:**
1. **Meropenem** - للحالات المقاومة لـ ESBL (فعالية 98%)
2. **Ceftriaxone** - للحالات الحساسة (فعالية 75%)
3. **Nitrofurantoin** - لالتهابات المسالك البولية البسيطة (فعالية 85%)

**ملاحظات مهمة:**
- تحقق من نتائج المزرعة قبل التعديل
- استخدم مبدأ De-escalation عند الإمكان
```

### Example 2: System Navigation

```
User: How do I add a new sample?

Bot: To add a new sample to the system:

**Steps:**
1. Navigate to `/samples` page
2. Click "Add New Sample" button
3. Fill in the required fields:
   - Patient ID
   - Bacteria type
   - Department
   - Collection date
4. Click "Save"

The sample will be added to the database and available for testing.
```

---

## 🔍 Testing the Integration

### Test Checklist:

#### Basic Functionality:
- [ ] Widget opens and closes
- [ ] Messages send successfully
- [ ] Responses display correctly
- [ ] Arabic text displays properly (RTL)
- [ ] English text displays properly (LTR)

#### Streaming:
- [ ] Toggle streaming checkbox works
- [ ] Messages stream in real-time
- [ ] Stop button cancels streaming
- [ ] Complete messages save to history

#### History:
- [ ] History loads on widget open
- [ ] Clear history button works
- [ ] Messages persist across sessions

#### Error Handling:
- [ ] Network errors show user-friendly message
- [ ] Invalid token shows auth error
- [ ] Empty messages are prevented

---

## 🐛 Troubleshooting

### Issue: "Cannot find module 'react-markdown'"

**Solution:**
```bash
cd Data_Analysis_Project/frontend
npm install react-markdown remark-gfm
```

### Issue: "Failed to fetch"

**Possible Causes:**
1. Backend not running
2. Wrong API URL in `.env.local`
3. CORS not configured

**Solution:**
```bash
# Check backend is running
cd Data_Analysis_Project
python manage.py runserver

# Verify API URL
echo $NEXT_PUBLIC_API_URL
```

### Issue: "401 Unauthorized"

**Solution:**
- Ensure user is logged in
- Check JWT token in localStorage
- Token may have expired, re-login required

### Issue: Streaming not working

**Possible Causes:**
1. Ollama not running
2. LLaMA model not loaded
3. Backend streaming endpoint error

**Solution:**
```bash
# Check Ollama status
ollama list

# Start Ollama if needed
ollama serve

# Test Ollama directly
curl http://localhost:11434/api/generate -d '{
  "model": "llama3.1",
  "prompt": "Hello"
}'
```

---

## 📱 Mobile Responsiveness

The ChatWidget is responsive and works on:
- ✅ Desktop (1920x1080+)
- ✅ Laptop (1366x768+)
- ✅ Tablet (768x1024+)
- ✅ Mobile (375x667+)

On mobile devices:
- Widget takes full screen when open
- Touch-friendly buttons
- Optimized keyboard handling

---

## 🎨 Customization

### Change Widget Colors:

Edit `ChatWidget.tsx`:

```tsx
// Header gradient
className="bg-gradient-to-r from-blue-600 to-blue-700"

// User message bubble
className="bg-blue-600 text-white"

// Bot message bubble
className="bg-white text-gray-900 border"
```

### Change Widget Position:

```tsx
// Bottom right (default)
className="fixed bottom-4 right-4 z-50"

// Bottom left
className="fixed bottom-4 left-4 z-50"

// Top right
className="fixed top-4 right-4 z-50"
```

### Change Widget Size:

```tsx
// Width
className="w-[420px]"  // Change to w-[500px] for wider

// Height
className="h-[600px]"  // Change to h-[700px] for taller
```

---

## 🔐 Security Considerations

### JWT Token Storage:
- Tokens stored in localStorage
- Automatically included in API requests
- Refresh token logic should be implemented

### CORS Configuration:
Ensure Django backend has proper CORS settings:

```python
# settings.py
CORS_ALLOWED_ORIGINS = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
]

CORS_ALLOW_CREDENTIALS = True
```

### API Rate Limiting:
Consider implementing rate limiting to prevent abuse:

```python
# Django REST Framework throttling
REST_FRAMEWORK = {
    'DEFAULT_THROTTLE_CLASSES': [
        'rest_framework.throttling.UserRateThrottle'
    ],
    'DEFAULT_THROTTLE_RATES': {
        'user': '100/hour'
    }
}
```

---

## 📊 Performance Optimization

### Lazy Loading:
The ChatWidget uses dynamic imports for better performance:

```tsx
// In your page component
import dynamic from 'next/dynamic';

const ChatWidget = dynamic(() => import('@/components/ChatWidget'), {
  ssr: false,
  loading: () => <div>Loading chat...</div>
});
```

### Message Pagination:
Currently loads last 20 messages. Adjust in `loadChatHistory()`:

```tsx
const response = await fetch(
  `${API_BASE_URL}/api/chatbot/history/?limit=50`  // Change limit
);
```

---

## 🎓 Next Steps

1. ✅ Install dependencies (`npm install react-markdown remark-gfm`)
2. ✅ Create `.env.local` with API URL
3. ✅ Start frontend (`npm run dev`)
4. ✅ Test chat functionality
5. ⏳ Implement additional features (voice input, file upload, etc.)
6. ⏳ Add analytics tracking
7. ⏳ Implement feedback system

---

## 📞 Support

For issues or questions:
1. Check this documentation
2. Review backend logs: `Data_Analysis_Project/logs/`
3. Check browser console for frontend errors
4. Verify Ollama is running: `ollama list`

---

**Last Updated:** 2024
**Version:** 1.0.0
**Status:** Ready for Integration ✅
