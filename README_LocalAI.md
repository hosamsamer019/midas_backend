# LocalAI Setup Guide - Free AI for Smart Antibiogram System

## Overview
This guide explains how to set up LocalAI, a free, self-hosted alternative to OpenAI ChatGPT for your antibiogram system. LocalAI eliminates API costs and quota limits while keeping your data private.

## Prerequisites
- Docker Desktop installed on your Windows machine
- At least 8GB RAM (recommended 16GB+)
- Internet connection for initial model download

## Installation Steps

### 1. Install Docker Desktop
1. Download Docker Desktop from: https://www.docker.com/products/docker-desktop
2. Run the installer and follow the setup wizard
3. Restart your computer after installation
4. Start Docker Desktop from the Start menu

### 2. Start LocalAI
Open Command Prompt or PowerShell and run:
```bash
cd Data_Analysis_Project
docker-compose -f docker-compose.localai.yml up -d
```

### 3. Wait for Model Download
- LocalAI will automatically download a default AI model
- This may take 5-15 minutes depending on your internet speed
- The first run is slow due to model download

### 4. Verify LocalAI is Running
- Open http://localhost:8080 in your browser
- You should see the LocalAI web interface
- Test the chatbot in your application

## Configuration

### Django Settings
The system is already configured to use LocalAI:
- **Base URL**: `http://localhost:8080/v1`
- **API Key**: `localai`
- **Model**: `gpt-3.5-turbo` (compatible)

### Files Modified
- `antibiogram/settings.py`: Added LocalAI configuration
- `chatbot/utils.py`: Updated to use LocalAI instead of OpenAI
- `docker-compose.localai.yml`: Docker configuration for LocalAI

## Troubleshooting

### LocalAI Not Starting
```bash
# Check if Docker is running
docker --version

# Check LocalAI container status
docker ps

# View LocalAI logs
docker-compose -f docker-compose.localai.yml logs
```

### Connection Issues
- Ensure LocalAI is running on port 8080
- Check firewall settings
- Restart the LocalAI container

### Performance Issues
- LocalAI may be slower than OpenAI initially
- Increase RAM allocation in Docker Desktop settings
- Consider using a smaller model if available

## Benefits
- ✅ **Zero API costs** - Completely free
- ✅ **Privacy** - All data stays on your machine
- ✅ **No quota limits** - No more "exceeded your current quota" errors
- ✅ **Offline capable** - Works without internet once model is downloaded

## Switching Back to OpenAI (Optional)
If you need to switch back to OpenAI:
1. Stop LocalAI: `docker-compose -f docker-compose.localai.yml down`
2. Update `antibiogram/settings.py` to use OpenAI configuration
3. Restart Django server

## Support
- LocalAI Documentation: https://localai.io/
- Docker Desktop: https://docs.docker.com/desktop/
- Report issues in your project repository
