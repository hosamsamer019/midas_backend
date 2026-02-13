# 🚀 Ollama Setup Guide for AI Assistant

## Overview
This guide will help you set up Ollama with LLaMA 3.1 model for the AI medical assistant.

---

## 📥 Step 1: Install Ollama

### Windows:
1. Download Ollama from: https://ollama.ai/download
2. Run the installer `OllamaSetup.exe`
3. Follow the installation wizard
4. Ollama will automatically start as a service

### Linux:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### macOS:
```bash
brew install ollama
```

---

## 🤖 Step 2: Download LLaMA 3.1 Model

Open a terminal/command prompt and run:

```bash
ollama pull llama3.1
```

This will download the LLaMA 3.1 model (approximately 4.7GB).

### Alternative Models (if needed):
```bash
# For smaller systems (2GB RAM minimum)
ollama pull llama3.1:8b

# For better performance (16GB RAM recommended)
ollama pull llama3.1:70b

# For Arabic-optimized version
ollama pull llama3.1
```

---

## ✅ Step 3: Verify Installation

### Check if Ollama is running:
```bash
ollama list
```

You should see `llama3.1` in the list.

### Test the model:
```bash
ollama run llama3.1 "مرحبا، ما هو المضاد الحيوي؟"
```

You should get an Arabic response about antibiotics.

---

## 🔧 Step 4: Configure Ollama for the Project

### Default Configuration:
- **URL**: `http://localhost:11434`
- **API Endpoint**: `http://localhost:11434/api/generate`
- **Model**: `llama3.1`

### Check if Ollama is accessible:
```bash
curl http://localhost:11434/api/tags
```

You should see a JSON response with available models.

---

## 🌐 Step 5: Test with Python

Create a test file `test_ollama.py`:

```python
import requests
import json

def test_ollama():
    url = "http://localhost:11434/api/generate"
    
    payload = {
        "model": "llama3.1",
        "prompt": "ما هو المضاد الحيوي الأفضل لعلاج E. coli؟",
        "stream": False
    }
    
    try:
        response = requests.post(url, json=payload, timeout=60)
        if response.status_code == 200:
            result = response.json()
            print("✅ Ollama is working!")
            print(f"Response: {result.get('response', 'No response')}")
            return True
        else:
            print(f"❌ Error: Status code {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_ollama()
```

Run it:
```bash
python test_ollama.py
```

---

## 🔥 Step 6: Start Ollama Service

### Windows:
Ollama runs automatically as a Windows service. To restart:
```bash
# Stop
net stop Ollama

# Start
net start Ollama
```

### Linux/macOS:
```bash
# Start Ollama server
ollama serve
```

Keep this terminal open while using the AI assistant.

---

## ⚙️ Advanced Configuration

### Change Default Port:
```bash
# Set environment variable
export OLLAMA_HOST=0.0.0.0:11434

# Then start Ollama
ollama serve
```

### Increase Context Window:
```bash
ollama run llama3.1 --ctx-size 4096
```

### GPU Acceleration:
Ollama automatically uses GPU if available (NVIDIA CUDA or AMD ROCm).

---

## 🐛 Troubleshooting

### Issue 1: "Connection refused"
**Solution**: Make sure Ollama service is running
```bash
# Windows
net start Ollama

# Linux/macOS
ollama serve
```

### Issue 2: "Model not found"
**Solution**: Download the model again
```bash
ollama pull llama3.1
```

### Issue 3: Slow responses
**Solutions**:
- Use smaller model: `ollama pull llama3.1:8b`
- Increase RAM allocation
- Close other applications
- Use GPU if available

### Issue 4: Arabic text not displaying correctly
**Solution**: LLaMA 3.1 supports Arabic natively. Ensure your terminal/IDE supports UTF-8 encoding.

---

## 📊 Performance Optimization

### Recommended System Requirements:
- **Minimum**: 8GB RAM, 10GB disk space
- **Recommended**: 16GB RAM, 20GB disk space, GPU with 6GB+ VRAM
- **Optimal**: 32GB RAM, 50GB disk space, GPU with 12GB+ VRAM

### Model Selection Guide:
| Model | Size | RAM Required | Best For |
|-------|------|--------------|----------|
| llama3.1:8b | 4.7GB | 8GB | Testing, development |
| llama3.1 | 4.7GB | 8GB | Production (default) |
| llama3.1:70b | 40GB | 64GB | Maximum accuracy |

---

## 🔗 Integration with Django

The project is already configured to use Ollama. Settings in `antibiogram/settings.py`:

```python
# Ollama Configuration
OLLAMA_BASE_URL = 'http://localhost:11434'
OLLAMA_MODEL = 'llama3.1'
```

---

## 📝 Testing the Integration

Run the Django server and test the chatbot:

```bash
# Start Django
cd Data_Analysis_Project
python manage.py runserver

# In another terminal, test the API
curl -X POST http://localhost:8000/api/chatbot/chat/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"message": "ما هو المضاد الحيوي؟"}'
```

---

## 🎯 Next Steps

1. ✅ Verify Ollama is running: `ollama list`
2. ✅ Test with Python script
3. ✅ Start Django server
4. ✅ Test chatbot API
5. ✅ Use the frontend chat interface

---

## 📚 Additional Resources

- **Ollama Documentation**: https://github.com/ollama/ollama
- **LLaMA 3.1 Model Card**: https://ollama.ai/library/llama3.1
- **API Reference**: https://github.com/ollama/ollama/blob/main/docs/api.md

---

## 🆘 Support

If you encounter issues:
1. Check Ollama logs: `ollama logs`
2. Restart Ollama service
3. Verify model is downloaded: `ollama list`
4. Check system resources (RAM, disk space)
5. Review Django logs for API errors

---

**Status**: ✅ Ready for production use with LLaMA 3.1
