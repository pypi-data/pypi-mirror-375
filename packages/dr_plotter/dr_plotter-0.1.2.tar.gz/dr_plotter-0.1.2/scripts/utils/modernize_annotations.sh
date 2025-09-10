#!/bin/bash
set -e

# Extract files that need __future__ import annotations from ruff FA100 violations
echo "Files that need __future__ import annotations:"
files_to_update=$(uv run ruff check --select FA100 --output-format=json 2>/dev/null | \
    jq -r '.[].filename' | sort -u)

if [ -z "$files_to_update" ]; then
    echo "No files need __future__ import annotations!"
    exit 0
fi

echo "$files_to_update"

echo -e "\nProceed with adding __future__ import annotations to these files? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

# Add __future__ import to each file
echo "Adding __future__ import annotations..."
echo "$files_to_update" | while read -r file; do
    echo "  Processing: $file"
    # Create temp file with __future__ import + original content
    { echo "from __future__ import annotations"; cat "$file"; } > "$file.tmp"
    mv "$file.tmp" "$file"
done

echo "✅ __future__ import annotations added!"

echo -e "\nProceed with modernizing type annotations (UP007) and cleaning up imports (F401,UP037)? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Skipping ruff fixes."
    exit 0
fi

echo "Running ruff fixes..."

# Modernize type annotations to use new syntax
echo "  Updating type annotations..."
uv run ruff check --select UP007 --fix --unsafe-fixes --quiet

# Clean up unused imports and optional typing imports
echo "  Cleaning up imports..." 
uv run ruff check --select F401,UP037 --fix --quiet

# Format code to fix line lengths and other style issues
echo "  Formatting code..."
uv run ruff format --quiet

echo "✅ Type annotation modernization complete!"