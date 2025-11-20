# Makefile for Coffee Script development

.PHONY: help setup test lint format clean build security all install run docs git-status git-diff git-log git-branch git-commit git-push git-pull git-sync git-add-commit git-acp

# Default target
help:
	@echo "Coffee Script Development Commands"
	@echo "================================="
	@echo ""
	@echo "Setup and Installation:"
	@echo "  setup     - Set up development environment"
	@echo "  install   - Install package in development mode"
	@echo ""
	@echo "Code Quality:"
	@echo "  format    - Format code with black, ruff, and isort"
	@echo "  lint      - Run linting tools (black, ruff, mypy)"
	@echo "  test      - Run test suite"
	@echo "  test-cov  - Run tests with coverage report"
	@echo "  security  - Run security checks"
	@echo ""
	@echo "Build and Clean:"
	@echo "  clean     - Clean build artifacts and cache files"
	@echo "  build     - Build package"
	@echo ""
	@echo "Workflows:"
	@echo "  all       - Run complete development workflow"
	@echo "  ci        - Run CI-like checks (lint + test + security)"
	@echo ""
	@echo "Application:"
	@echo "  run       - Run the coffee script"
	@echo "  docs      - Generate documentation"
	@echo ""
	@echo "Git Management:"
	@echo "  git-status      - Show git status"
	@echo "  git-diff        - Show uncommitted changes"
	@echo "  git-log         - Show recent commits"
	@echo "  git-branch      - Show current branch and branches"
	@echo "  git-commit      - Commit staged changes (use MSG='commit message')"
	@echo "  git-push        - Push changes to remote"
	@echo "  git-pull        - Pull changes from remote"
	@echo "  git-sync        - Pull, then push changes"
	@echo "  git-add-commit  - Add all and commit (use MSG='commit message')"
	@echo "  git-acp         - Add, commit, and push (use MSG='commit message')"

# Setup development environment
setup:
	@echo "🔧 Setting up development environment..."
	pip install -e .[dev]
	pre-commit install
	pre-commit install --hook-type commit-msg
	@echo "✅ Development environment ready!"

# Install package in development mode
install:
	pip install -e .

# Format code
format:
	@echo "🎨 Formatting code..."
	black src/ tests/
	ruff --fix src/ tests/
	isort src/ tests/
	@echo "✅ Code formatted!"

# Run linting
lint:
	@echo "🔍 Running linting checks..."
	black --check src/ tests/
	ruff check src/ tests/
	mypy src/coffee/
	@echo "✅ Linting complete!"

# Run tests
test:
	@echo "🧪 Running tests..."
	pytest tests/ -q
	@echo "✅ Tests complete!"

# Run tests with coverage
test-cov:
	@echo "🧪 Running tests with coverage..."
	pytest tests/ --cov=src/coffee --cov-report=html --cov-report=term
	@echo "✅ Tests with coverage complete!"
	@echo "📊 Coverage report available in htmlcov/index.html"

# Run security checks
security:
	@echo "🔒 Running security checks..."
	bandit -r src/
	pip-audit
	@echo "✅ Security checks complete!"

# Clean build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .pytest_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .mypy_cache -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name .ruff_cache -exec rm -rf {} + 2>/dev/null || true
	rm -rf htmlcov/
	rm -f .coverage
	@echo "✅ Cleanup complete!"

# Build package
build: clean
	@echo "📦 Building package..."
	python -m build
	@echo "✅ Package built!"

# Run complete development workflow
all: format lint test-cov security build
	@echo "🎉 Complete development workflow finished!"

# Run CI-like checks
ci: lint test security
	@echo "🤖 CI checks complete!"

# Run the application
run:
	@echo "☕ Starting Coffee Script..."
	python -m coffee

# Generate documentation (placeholder for future docs)
docs:
	@echo "📚 Documentation generation not yet implemented"
	@echo "   Consider adding sphinx or mkdocs in the future"

# Development server with auto-reload (if needed in future)
dev:
	@echo "🔄 Development mode not yet implemented"
	@echo "   This could include file watching and auto-restart"

# Release preparation
release-check: all
	@echo "🚀 Release readiness check..."
	@echo "✅ All checks passed - ready for release!"

# Quick development cycle
quick: format test
	@echo "⚡ Quick development cycle complete!"

# ==========================================
# Git Management
# ==========================================

# Show git status
git-status:
	@echo "📊 Git Status:"
	@git status

# Show uncommitted changes
git-diff:
	@echo "📝 Uncommitted changes:"
	@git diff
	@echo ""
	@echo "📝 Staged changes:"
	@git diff --cached

# Show recent commits
git-log:
	@echo "📜 Recent commits:"
	@git log --oneline --graph --decorate -10

# Show current branch and all branches
git-branch:
	@echo "🌿 Current branch:"
	@git branch --show-current
	@echo ""
	@echo "🌿 All branches:"
	@git branch -a

# Commit staged changes (requires MSG variable)
git-commit:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a commit message using MSG='your message'"; \
		echo "   Example: make git-commit MSG='Add new feature'"; \
		exit 1; \
	fi
	@echo "💾 Committing changes..."
	@git commit -m "$(MSG)"
	@echo "✅ Changes committed!"

# Push changes to remote
git-push:
	@echo "⬆️  Pushing changes to remote..."
	@git push
	@echo "✅ Changes pushed!"

# Pull changes from remote
git-pull:
	@echo "⬇️  Pulling changes from remote..."
	@git pull
	@echo "✅ Changes pulled!"

# Sync with remote (pull then push)
git-sync:
	@echo "🔄 Syncing with remote..."
	@git pull
	@git push
	@echo "✅ Sync complete!"

# Add all changes and commit (shortcut)
git-add-commit:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a commit message using MSG='your message'"; \
		echo "   Example: make git-add-commit MSG='Add new feature'"; \
		exit 1; \
	fi
	@echo "➕ Adding all changes..."
	@git add .
	@echo "💾 Committing changes..."
	@git commit -m "$(MSG)"
	@echo "✅ Changes added and committed!"

# Complete git workflow: add, commit, and push
git-acp:
	@if [ -z "$(MSG)" ]; then \
		echo "❌ Error: Please provide a commit message using MSG='your message'"; \
		echo "   Example: make git-acp MSG='Add new feature'"; \
		exit 1; \
	fi
	@echo "➕ Adding all changes..."
	@git add .
	@echo "💾 Committing changes..."
	@git commit -m "$(MSG)"
	@echo "⬆️  Pushing changes..."
	@git push
	@echo "✅ Complete! Changes added, committed, and pushed!"