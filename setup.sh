#!/bin/bash

# Setup script for Agent Load Balancer System

echo "🚀 Setting up Agent Load Balancer System..."
echo ""

# Check if Docker is installed
if command -v docker &> /dev/null; then
    echo "✅ Docker is installed"
else
    echo "❌ Docker is not installed. Please install Docker first."
    echo "   Visit: https://docs.docker.com/get-docker/"
fi

# Check if Docker Compose is installed
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose is installed"
else
    echo "❌ Docker Compose is not installed"
fi

echo ""
echo "Select deployment method:"
echo "1) Docker (recommended)"
echo "2) Local development"
read -p "Enter choice [1-2]: " choice

case $choice in
    1)
        echo ""
        echo "🐳 Starting with Docker..."
        docker-compose up --build
        ;;
    2)
        echo ""
        echo "📦 Setting up local development environment..."
        
        # Backend setup
        echo ""
        echo "Setting up Backend..."
        cd backend
        
        if command -v python3 &> /dev/null; then
            echo "✅ Python is installed"
            python3 -m venv venv
            source venv/bin/activate
            pip install -r requirements.txt
            echo "✅ Backend dependencies installed"
        else
            echo "❌ Python is not installed. Please install Python 3.11+"
            exit 1
        fi
        
        cd ..
        
        # Frontend setup
        echo ""
        echo "Setting up Frontend..."
        cd frontend
        
        if command -v node &> /dev/null; then
            echo "✅ Node.js is installed"
            npm install
            echo "✅ Frontend dependencies installed"
        else
            echo "❌ Node.js is not installed. Please install Node.js 20+"
            exit 1
        fi
        
        cd ..
        
        echo ""
        echo "✅ Setup complete!"
        echo ""
        echo "To start the backend:"
        echo "  cd backend"
        echo "  source venv/bin/activate"
        echo "  python main.py"
        echo ""
        echo "To start the frontend (in a new terminal):"
        echo "  cd frontend"
        echo "  npm run dev"
        echo ""
        echo "Access the application:"
        echo "  Frontend: http://localhost:3000"
        echo "  Backend API: http://localhost:8000"
        echo "  API Docs: http://localhost:8000/docs"
        ;;
    *)
        echo "Invalid choice"
        exit 1
        ;;
esac
