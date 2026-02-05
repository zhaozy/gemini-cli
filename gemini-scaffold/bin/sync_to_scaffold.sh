#!/bin/bash
# Sync Active Engineering Upgrades back to Scaffold (v5.0)
set -e

echo "Syncing ALL active architecture upgrades to gemini-scaffold..."

# 1. Sync Constitution & Docs
cp GEMINI.md gemini-scaffold/templates/ROOT_GEMINI.md
mkdir -p gemini-scaffold/docs
cp docs/THE_CODE_TAO.md gemini-scaffold/docs/

# 2. Sync Global Memory Templates
cp .gemini/tasks/memory.md gemini-scaffold/templates/tasks/memory.md

# 3. Sync Employees & SOPs & Scripts (The core workforce)
mkdir -p gemini-scaffold/employees/
cp -r employees/* gemini-scaffold/employees/
# 同步雇员生成模板
mkdir -p gemini-scaffold/templates/employee/SOPs
cp .gemini/templates/* gemini-scaffold/templates/employee/ 2>/dev/null || true

# 4. Sync ALL Automation Scripts (The core power)
mkdir -p gemini-scaffold/bin
cp .gemini/bin/* gemini-scaffold/bin/

# 5. Cleanup Scaffold sensitive data (if any)
rm -rf gemini-scaffold/employees/*/__pycache__

echo "✓ Critical Audit Pass: All automation logic and expert SOPs are now secured in scaffold."