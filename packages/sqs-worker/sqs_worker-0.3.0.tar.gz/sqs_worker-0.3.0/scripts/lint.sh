#!/bin/bash

# Linting script for sqs-worker project
# This script runs ruff linter and formatter

set -e

echo "🔍 Running ruff linter..."
uv run ruff check .

echo "🔧 Running ruff formatter..."
uv run ruff format --check .

echo "✅ All checks passed!"
