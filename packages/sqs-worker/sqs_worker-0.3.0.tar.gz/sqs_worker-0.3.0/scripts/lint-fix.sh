#!/bin/bash

# Auto-fix script for sqs-worker project
# This script runs ruff linter with auto-fix and formats the code

set -e

echo "🔧 Running ruff linter with auto-fix..."
uv run ruff check --fix .

echo "🎨 Running ruff formatter..."
uv run ruff format .

echo "✅ Code has been linted and formatted!"
