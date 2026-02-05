#!/bin/bash
# Gemini Digital Workforce Health Checker
set -e

echo "Checking health of your digital workforce..."

# 1. Check Python dependencies
REQUIRED_LIBS=("pandas" "numpy" "tabulate" "requests")
MISSING_LIBS=()

for lib in "${REQUIRED_LIBS[@]}"; do
    if ! python3 -c "import $lib" &>/dev/null; then
        MISSING_LIBS+=("$lib")
    fi
done

if [ ${#MISSING_LIBS[@]} -gt 0 ]; then
    echo "Missing libraries: ${MISSING_LIBS[*]}"
    echo "Installing missing dependencies via uv..."
    uv pip install "${MISSING_LIBS[@]}"
else
    echo "✓ All Python dependencies are met."
fi

# 2. Check Execution Permissions
echo "Fixing script permissions..."
find employees/ -name "*.py" -exec chmod +x {} +
find employees/ -name "*.sh" -exec chmod +x {} +

echo "✓ Health check complete. Your experts are ready for work."
