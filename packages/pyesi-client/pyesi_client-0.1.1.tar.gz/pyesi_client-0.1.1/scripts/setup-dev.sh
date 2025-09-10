#!/bin/bash

# Development environment setup script for pyesi-client
# This script sets up all necessary tools for development including:
# - Python dependencies with uv
# - Git hooks with pre-commit (includes commitlint)
# - Type checking with pyright

set -e

echo "🚀 Setting up development environment for pyesi-client..."

# Check if we're in the right directory
if [ ! -f "pyproject.toml" ]; then
    echo "❌ Error: This script must be run from the project root directory"
    exit 1
fi

# Install Python dependencies
echo "📦 Installing Python dependencies with uv..."
if ! command -v uv >/dev/null 2>&1 && ! which uv >/dev/null 2>&1; then
    echo "❌ Error: uv is not installed. Please install uv first."
    echo "   Install with: curl -LsSf https://astral.sh/uv/install.sh | sh"
    exit 1
fi

uv sync
echo "✅ Python dependencies installed"

# Initialize pre-commit (includes commitlint for commit-msg validation)
echo "🪝 Setting up pre-commit hooks..."
uv run pre-commit install
uv run pre-commit install --hook-type commit-msg
echo "✅ Pre-commit hooks installed (includes commitlint for commit messages)"

# Create a simple test to verify everything works
echo "🧪 Running verification tests..."

# Test ruff
echo "  Testing ruff..."
uv run ruff check --quiet .
uv run ruff format --check --quiet .
echo "  ✅ Ruff checks passed"

# Test pyright
echo "  Testing pyright..."
uv run pyright . > /dev/null 2>&1 || echo "  ⚠️  Pyright found some issues (this is normal for initial setup)"

# Test pytest
if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "  Testing pytest..."
    uv run pytest --quiet
    echo "  ✅ Tests passed"
fi

echo ""
echo "🎉 Development environment setup complete!"
echo ""
echo "Available commands:"
echo "  uv run pytest              # Run tests"
echo "  uv run pytest --cov        # Run tests with coverage"
echo "  uv run ruff check          # Run linting"
echo "  uv run ruff format         # Format code"
echo "  uv run pyright             # Run type checking"
echo "  uv run pre-commit run      # Run all pre-commit hooks"
echo ""
echo "Git hooks are now active:"
echo "  - Pre-commit: Runs ruff, pyright, and pytest before commits"
echo "  - Commit-msg: Validates commit message format with commitlint"
echo ""
echo "Happy coding! 🐍✨"