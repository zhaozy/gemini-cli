#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Gemini CLI Cognitive Scaffold Installer (Project MNEMOSYNE) ===${NC}"

# 1. Check for uv (The Astral Stack)
if ! command -v uv &> /dev/null; then
    echo "Installing uv..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo -e "${GREEN}✓ uv is already installed.${NC}"
fi

# 2. Check for gh (GitHub CLI)
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI (gh)..."
    brew install gh || echo "Please install GitHub CLI manually."
else
    echo -e "${GREEN}✓ gh is already installed.${NC}"
fi

# 3. Setup Global Structure
echo "Deploying cognitive architecture..."
mkdir -p .gemini/tasks
cp gemini-scaffold/templates/tasks/* .gemini/tasks/
cp gemini-scaffold/templates/ROOT_GEMINI.md GEMINI.md

# 4. Deploy Digital Workforce (Employees)
mkdir -p employees
if [ -d "gemini-scaffold/employees" ]; then
    cp -r gemini-scaffold/employees/* employees/
    echo -e "${GREEN}✓ Digital Workforce (employees/) successfully deployed.${NC}"
fi

# 5. Initialize Projects Container
mkdir -p projects
echo -e "${GREEN}✓ Projects container (projects/) initialized.${NC}"

# 6. Create automation scripts
mkdir -p .gemini/bin
cp gemini-scaffold/bin/* .gemini/bin/ 2>/dev/null || true
chmod +x .gemini/bin/* 2>/dev/null || true

echo -e "${BLUE}=== Setup Complete ===${NC}"
echo "You are now ready. To hire an expert or create a project, use scripts in .gemini/bin/."
if ! gh auth status &>/dev/null; then
    echo -e "${BLUE}⚠ Reminder: Run 'gh auth login -p ssh -w' to enable cloud automation.${NC}"
fi
