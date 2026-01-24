@echo off
REM Setup script for Agent Load Balancer System (Windows)

echo Setting up Agent Load Balancer System...
echo.

REM Check if Docker is installed
where docker >nul 2>nul
if %errorlevel% equ 0 (
    echo [OK] Docker is installed
) else (
    echo [ERROR] Docker is not installed. Please install Docker first.
    echo Visit: https://docs.docker.com/get-docker/
)

echo.
echo Select deployment method:
echo 1) Docker (recommended)
echo 2) Local development
set /p choice="Enter choice [1-2]: "

if "%choice%"=="1" (
    echo.
    echo Starting with Docker...
    docker-compose up --build
) else if "%choice%"=="2" (
    echo.
    echo Setting up local development environment...
    
    REM Backend setup
    echo.
    echo Setting up Backend...
    cd backend
    
    where python >nul 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Python is installed
        python -m venv venv
        call venv\Scripts\activate
        pip install -r requirements.txt
        echo [OK] Backend dependencies installed
    ) else (
        echo [ERROR] Python is not installed. Please install Python 3.11+
        exit /b 1
    )
    
    cd ..
    
    REM Frontend setup
    echo.
    echo Setting up Frontend...
    cd frontend
    
    where node >nul 2>nul
    if %errorlevel% equ 0 (
        echo [OK] Node.js is installed
        npm install
        echo [OK] Frontend dependencies installed
    ) else (
        echo [ERROR] Node.js is not installed. Please install Node.js 20+
        exit /b 1
    )
    
    cd ..
    
    echo.
    echo [OK] Setup complete!
    echo.
    echo To start the backend:
    echo   cd backend
    echo   venv\Scripts\activate
    echo   python main.py
    echo.
    echo To start the frontend (in a new terminal):
    echo   cd frontend
    echo   npm run dev
    echo.
    echo Access the application:
    echo   Frontend: http://localhost:3000
    echo   Backend API: http://localhost:8000
    echo   API Docs: http://localhost:8000/docs
) else (
    echo Invalid choice
    exit /b 1
)
