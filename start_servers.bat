@echo off
echo Starting MediSwift Platform...
echo.

REM Start Django backend server
echo Starting Django backend server...
start "Django Backend" cmd /k "cd backend && venv\Scripts\activate && python manage.py runserver"

REM Wait a moment for backend to start
timeout /t 3 /nobreak >nul

REM Start React frontend server
echo Starting React frontend server...
start "React Frontend" cmd /k "cd frontend && npm start"

echo.
echo Both servers are starting...
echo Backend: http://localhost:8000
echo Frontend: http://localhost:3000
echo Admin Panel: http://localhost:8000/admin
echo.
echo Press any key to exit this window...
pause >nul
