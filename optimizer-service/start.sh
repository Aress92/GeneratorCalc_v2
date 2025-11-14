#!/bin/bash

###############################################################################
# Startup Script for SLSQP Optimizer Microservice (Linux/Mac)
###############################################################################

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  SLSQP Optimizer Microservice Startup                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Check Python version
echo -e "${YELLOW}[1/5]${NC} Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}ERROR: python3 not found. Please install Python 3.11+${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | awk '{print $2}')
echo -e "${GREEN}✓${NC} Python ${PYTHON_VERSION} found"

# Check if virtual environment exists
echo ""
echo -e "${YELLOW}[2/5]${NC} Checking virtual environment..."
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠ Virtual environment not found. Creating...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
else
    echo -e "${GREEN}✓${NC} Virtual environment found"
fi

# Activate virtual environment
echo ""
echo -e "${YELLOW}[3/5]${NC} Activating virtual environment..."
source venv/bin/activate
echo -e "${GREEN}✓${NC} Virtual environment activated"

# Install/update dependencies
echo ""
echo -e "${YELLOW}[4/5]${NC} Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Dependencies installed"

# Start the service
echo ""
echo -e "${YELLOW}[5/5]${NC} Starting optimizer service..."
echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║  Service Starting...                                      ║${NC}"
echo -e "${GREEN}║  API Docs: http://127.0.0.1:8001/docs                     ║${NC}"
echo -e "${GREEN}║  Health: http://127.0.0.1:8001/health                     ║${NC}"
echo -e "${GREEN}║  Press Ctrl+C to stop                                     ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════╝${NC}"
echo ""

# Run the service
python run.py "$@"
