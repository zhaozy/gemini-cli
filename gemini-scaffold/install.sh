#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}=== Gemini CLI Cognitive Scaffold Installer ===${NC}"

# 1. Check for uv
if ! command -v uv &> /dev/null; then
    echo "Installing uv (The Astral Stack)..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
else
    echo -e "${GREEN}✓ uv is already installed.${NC}"
fi

# 2. Check for gh (GitHub CLI)
if ! command -v gh &> /dev/null; then
    echo "Installing GitHub CLI (gh) via Homebrew..."
    brew install gh
else
    echo -e "${GREEN}✓ gh is already installed.${NC}"
fi

# Ensure gh is logged in
if ! gh auth status &>/dev/null; then
    echo -e "${BLUE}⚠ 请在终端执行 'gh auth login -p ssh -w' 以授权自动化仓库创建能力。${NC}"
fi

# 2. Setup Root Structure
TARGET_DIR=$(pwd)
echo "Initializing Gemini environment in: $TARGET_DIR"

# Create .gemini/tasks
mkdir -p .gemini/tasks
cp gemini-scaffold/templates/tasks/* .gemini/tasks/

# Create GEMINI.md
cp gemini-scaffold/templates/ROOT_GEMINI.md GEMINI.md

# 3. Deploy Digital Workforce (Employees)
mkdir -p employees
if [ -d "gemini-scaffold/employees" ]; then
    cp -r gemini-scaffold/employees/* employees/
fi

# 4. Initialize Projects Container
mkdir -p projects

# 5. Create helper scripts
mkdir -p .gemini/bin

# Helper: New Employee
cat > .gemini/bin/new_employee <<EOF
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: \$0 <employee_name>"
    exit 1
fi
EMP_NAME=\$1
mkdir -p employees/\$EMP_NAME/SOPs
cp gemini-scaffold/templates/employee/manifest.json employees/\$EMP_NAME/
cp gemini-scaffold/templates/employee/commands.json employees/\$EMP_NAME/
cp gemini-scaffold/templates/employee/SOPs/* employees/\$EMP_NAME/SOPs/
echo "Hired new employee: \$EMP_NAME"
EOF

# Helper: New Project
cat > .gemini/bin/new_project <<EOF
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: \$0 <project_name>"
    exit 1
fi
PROJECT_NAME=\$1
mkdir -p projects/\$PROJECT_NAME/.gemini/tasks
sed "s/{{PROJECT_NAME}}/\$PROJECT_NAME/g" gemini-scaffold/templates/PROJECT_GEMINI.md > projects/\$PROJECT_NAME/GEMINI.md
touch projects/\$PROJECT_NAME/.gemini/tasks/{current_task,memory,implementation_plan,walkthrough}.md
echo "Initialized project: \$PROJECT_NAME in projects/ directory."
EOF

chmod +x .gemini/bin/new_employee .gemini/bin/new_project

echo -e "${GREEN}✓ Setup Complete. Architecture is now Project-Aware.${NC}"