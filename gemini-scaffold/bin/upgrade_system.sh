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

# 2. Setup Root Structure
TARGET_DIR=$(pwd)
echo "Initializing Gemini environment in: $TARGET_DIR"

# Create .gemini/tasks
mkdir -p .gemini/tasks
cp gemini-scaffold/templates/tasks/* .gemini/tasks/
echo -e "${GREEN}✓ Global cognition layer (.gemini/tasks) initialized.${NC}"

# Create GEMINI.md
cp gemini-scaffold/templates/ROOT_GEMINI.md GEMINI.md
echo -e "${GREEN}✓ Global Constitution (GEMINI.md) deployed.${NC}"

# Create _skills
mkdir -p _skills
touch _skills/.gitkeep
echo -e "${GREEN}✓ Skills registry (_skills/) created.${NC}"

# 4. Deploy Digital Workforce (Employees)
mkdir -p employees
if [ -d "gemini-scaffold/employees" ]; then
    cp -r gemini-scaffold/employees/* employees/
    echo -e "${GREEN}✓ Digital Workforce (employees/) deployed.${NC}"
fi

# 5. Create helper scripts
mkdir -p .gemini/bin
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
chmod +x .gemini/bin/new_employee
#!/bin/bash
if [ -z "\$1" ]; then
    echo "Usage: \$0 <project_name>"
    exit 1
fi
PROJECT_NAME=\$1
mkdir -p \$PROJECT_NAME/.gemini/tasks
sed "s/{{PROJECT_NAME}}/\$PROJECT_NAME/g" gemini-scaffold/templates/PROJECT_GEMINI.md > \$PROJECT_NAME/GEMINI.md
touch \$PROJECT_NAME/.gemini/tasks/{current_task,memory,implementation_plan,walkthrough}.md
echo "Initialized project: \$PROJECT_NAME"
EOF
chmod +x .gemini/bin/new_project

echo -e "${BLUE}=== Setup Complete ===${NC}"
echo "You are now ready. To start a new project, run:"
echo "  .gemini/bin/new_project my_new_analysis"
