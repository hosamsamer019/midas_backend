@echo off
echo Starting Smart Antibiogram System Servers...
echo.

echo Starting Backend Server (Django)...
start "Django Backend" cmd /k "cd /d %~dp0 && python manage.py runserver"

timeout /t 3 /nobreak > nul

echo Starting Frontend Server (Next.js)...
start "Next.js Frontend" cmd /k "cd /d %~dp0\frontend && npm run dev"

echo.
echo Servers started successfully!
echo - Backend: http://127.0.0.1:8000
echo - Frontend: http://localhost:3000
echo.
echo Press any key to exit...
pause > nul
