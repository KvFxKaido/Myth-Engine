#!/bin/bash
# Sovwren IDE Launcher
# Friction-free first-run experience

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
DIM='\033[2m'
NC='\033[0m' # No Color

echo ""
echo -e "${DIM}Sovwren IDE${NC}"
echo -e "${DIM}Partnership-First Interface${NC}"
echo ""

# Check Python version
PYTHON_CMD=""
if command -v python3 &> /dev/null; then
    PYTHON_CMD="python3"
elif command -v python &> /dev/null; then
    PYTHON_CMD="python"
else
    echo -e "${RED}Python not found. Please install Python 3.8+${NC}"
    exit 1
fi

PYTHON_VERSION=$($PYTHON_CMD -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$($PYTHON_CMD -c 'import sys; print(sys.version_info.minor)')

if [ "$PYTHON_MAJOR" -lt 3 ] || ([ "$PYTHON_MAJOR" -eq 3 ] && [ "$PYTHON_MINOR" -lt 8 ]); then
    echo -e "${RED}Python 3.8+ required (found $PYTHON_VERSION)${NC}"
    exit 1
fi

echo -e "${DIM}Python $PYTHON_VERSION${NC}"

# Install dependencies if needed
install_deps() {
    echo -e "${DIM}Checking dependencies...${NC}"

    # Check if venv exists, create if not
    if [ ! -d "venv" ]; then
        echo -e "${YELLOW}Creating virtual environment...${NC}"
        $PYTHON_CMD -m venv venv
    fi

    # Activate venv
    source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null

    # Install requirements
    if [ -f "requirements.txt" ]; then
        if [ -f "requirements.lock" ]; then
            pip install -q -r requirements.lock 2>/dev/null || pip install -r requirements.lock
        else
            pip install -q -r requirements.txt 2>/dev/null || pip install -r requirements.txt
        fi
    fi

    echo -e "${GREEN}Dependencies ready${NC}"
}

# Check LM Studio connection
check_lmstudio() {
    echo -e "${DIM}Checking LM Studio...${NC}"

    # Try to connect to LM Studio
    RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:1234/v1/models 2>/dev/null || echo "000")

    if [ "$RESPONSE" = "200" ]; then
        echo -e "${GREEN}LM Studio connected${NC}"
        return 0
    else
        echo -e "${YELLOW}LM Studio not detected at http://127.0.0.1:1234${NC}"
        echo ""
        echo -e "${DIM}Please start LM Studio and enable the local server:${NC}"
        echo -e "${DIM}  1. Open LM Studio${NC}"
        echo -e "${DIM}  2. Go to Local Server tab${NC}"
        echo -e "${DIM}  3. Load a model${NC}"
        echo -e "${DIM}  4. Click 'Start Server'${NC}"
        echo ""
        read -p "Press Enter when ready (or Ctrl+C to exit)..."
        return 0
    fi
}

# Run the IDE
run_ide() {
    echo ""
    echo -e "${DIM}Launching Sovwren IDE...${NC}"
    echo ""

    # Activate venv if exists
    if [ -d "venv" ]; then
        source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
    fi

    $PYTHON_CMD -B sovwren_ide.py
}

# Main
install_deps
check_lmstudio
run_ide
