@echo off
echo Starting LocalAI for Smart Antibiogram System...
echo.
echo This will start LocalAI in the background using Docker.
echo The first run will download AI models (may take 5-15 minutes).
echo.
echo Press any key to continue...
pause > nul

cd /d "%~dp0"

echo Checking if Docker is running...
docker --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker is not installed or not in PATH.
    echo Please install Docker Desktop from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Starting LocalAI container...
docker-compose -f docker-compose.localai.yml up -d

if errorlevel 1 (
    echo ERROR: Failed to start LocalAI.
    echo Please check Docker is running and try again.
    pause
    exit /b 1
)

echo.
echo LocalAI started successfully!
echo.
echo - LocalAI will be available at: http://localhost:8080
echo - Your antibiogram chatbot will now use LocalAI instead of OpenAI
echo - No more API costs or quota limits!
echo.
echo Press any key to exit...
pause > nul
