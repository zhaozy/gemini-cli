#!/bin/bash
# Sync Active Engineering Upgrades back to Scaffold
set -e

echo "Syncing active system changes to gemini-scaffold..."

# 1. Sync Constitution
cp GEMINI.md gemini-scaffold/templates/ROOT_GEMINI.md

# 2. Sync Global Memory Templates (excluding specific personal task data)
cp .gemini/tasks/memory.md gemini-scaffold/templates/tasks/memory.md

# 3. Sync Employees & Templates (including SOPs and Scripts)
mkdir -p gemini-scaffold/employees/
cp -r employees/* gemini-scaffold/employees/ 2>/dev/null || true
cp .gemini/templates/* gemini-scaffold/templates/employee/ 2>/dev/null || true

# 4. Sync Scripts
cp .gemini/bin/hire_expert.sh gemini-scaffold/bin/ 2>/dev/null || true

echo "✓ Scaffold is now in sync with active project architecture."
