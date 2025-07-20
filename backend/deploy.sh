#!/bin/bash

# Kembang Kopi Deployment Script
# Usage: ./deploy.sh [production|development]

ENV=${1:-production}

echo "🚀 Starting Kembang Kopi deployment for $ENV environment..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if .env file exists
if [ ! -f ".env" ]; then
    print_error ".env file not found!"
    print_warning "Please copy .env.example to .env and fill in your values"
    cp .env.example .env
    print_status "Created .env from template. Please edit it with your values."
    exit 1
fi

print_status "Environment file found ✓"

# Check Python version
python_version=$(python3 --version 2>&1)
print_status "Python version: $python_version"

# Create virtual environment if not exists
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Install requirements
print_status "Installing Python dependencies..."
pip install -r requirements.txt

# Validate configuration
print_status "Validating configuration..."
python3 -c "from config.config import Config; Config.validate_config(); print('✓ Configuration valid')"

if [ $? -ne 0 ]; then
    print_error "Configuration validation failed!"
    exit 1
fi

# Set environment variable
export ENVIRONMENT=$ENV

if [ "$ENV" = "production" ]; then
    print_status "Starting production server..."
    print_warning "Make sure your domains are pointing to this server"
    print_warning "Make sure SSL certificates are configured"
    print_warning "Make sure Nginx reverse proxy is configured"
    
    # Start with gunicorn for production
    if command -v gunicorn &> /dev/null; then
        gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    else
        print_warning "Gunicorn not found, installing..."
        pip install gunicorn
        gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
    fi
else
    print_status "Starting development server..."
    python3 main.py
fi
