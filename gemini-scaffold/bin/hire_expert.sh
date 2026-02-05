#!/bin/bash
if [ -z "$1" ]; then
    echo "Usage: $0 <employee_name>"
    exit 1
fi
EMP_NAME=$1
mkdir -p employees/$EMP_NAME/SOPs
cp .gemini/templates/manifest.json employees/$EMP_NAME/
cp .gemini/templates/commands.json employees/$EMP_NAME/
cp .gemini/templates/core_logic.md employees/$EMP_NAME/SOPs/
echo "Successfully hired new employee: $EMP_NAME in current project."
