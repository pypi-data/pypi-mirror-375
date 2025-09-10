#!/bin/bash
set -e

echo "Finding E501 line length violations..."

# Get files with E501 violations
files_with_violations=$(uv run ruff check --select E501 --output-format=json 2>/dev/null | \
    jq -r '.[].filename' | sort -u)

if [ -z "$files_with_violations" ]; then
    echo "No E501 violations found!"
    exit 0
fi

echo "Files with line length violations:"
echo "$files_with_violations"

echo -e "\nProceed with automated line length fixes? (y/N)"
read -r response
if [[ ! "$response" =~ ^[Yy]$ ]]; then
    echo "Aborted."
    exit 0
fi

echo -e "\nKeep files with syntax errors for debugging? (y/N)"
read -r debug_response
debug_mode=false
if [[ "$debug_response" =~ ^[Yy]$ ]]; then
    debug_mode=true
    echo "Debug mode: Will keep modified files even if they have syntax errors"
fi

# Process each file
echo "Processing files..."
echo "$files_with_violations" | while read -r file; do
    echo "  Processing: $file"
    
    # Create backup
    cp "$file" "$file.backup"
    
    # Apply general fixes using sed
    sed -i '' \
        -e 's/\(help="[^"]*\)\. \([^"]*"\)/\1. "\n        "\2/' \
        -e 's/\(help="[^"]*\) (e\.g\., \([^"]*"\)/\1 "\n        "(e.g., \2/' \
        -e 's/\(help="[^"]*\)\. Use \([^"]*"\)/\1. "\n        "Use \2/' \
        -e 's/\(description="[^"]*\) - \([^"]*"\)/\1 "\n        "- \2/' \
        -e 's/\(f"[^"]*\): \([^"]*"\)/\1: "\n            f"\2/' \
        "$file"
    
    # Check if the file is still valid Python
    if ! python -m py_compile "$file" 2>/dev/null; then
        if [ "$debug_mode" = true ]; then
            echo "    ⚠️  Syntax error introduced, keeping for debug (backup at $file.backup)"
        else
            echo "    ⚠️  Syntax error introduced, reverting..."
            mv "$file.backup" "$file"
        fi
    else
        echo "    ✅ Fixed"
        rm "$file.backup"
    fi
done

echo -e "\nRunning final formatting..."
uv run ruff format --quiet

echo "✅ Line length fixing complete!"
echo "Check remaining violations with: uv run ruff check --select E501"
