# Makefile for Terra Command AI development

.PHONY: help install install-dev test test-verbose test-coverage lint format clean clean-all build publish docs check dev-setup

# Default target
help:
	@echo "Terra Command AI Development Commands:"
	@echo ""
	@echo "Installation:"
	@echo "  install       Install Terra Command AI"
	@echo "  install-dev   Install Terra Command AI in development mode"
	@echo "  dev-setup     Set up development environment"
	@echo ""
	@echo "Testing:"
	@echo "  test          Run all tests"
	@echo "  test-verbose  Run tests with verbose output"
	@echo "  test-coverage Run tests with coverage report"
	@echo ""
	@echo "Code Quality:"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  check         Run all quality checks"
	@echo ""
	@echo "Build & Deploy:"
	@echo "  clean         Clean build artifacts"
	@echo "  clean-all     Clean all artifacts including caches"
	@echo "  build         Build distribution packages"
	@echo "  publish       Publish to PyPI"
	@echo ""
	@echo "Development:"
	@echo "  docs          Generate documentation"

# Installation
install:
	pip install .

install-dev:
	pip install -e .[dev]

dev-setup: clean-all
	python -m venv venv
	. venv/bin/activate && pip install -e .[dev]
	@echo "Development environment set up. Run 'source venv/bin/activate' to activate."

# Testing
test:
	python -m pytest tai/tests/

test-verbose:
	python -m pytest tai/tests/ -v

test-coverage:
	python -m pytest tai/tests/ --cov=tai --cov-report=html --cov-report=term

# Code Quality
lint:
	@echo "Running flake8..."
	flake8 tai/ --count --select=E9,F63,F7,F82 --show-source --statistics
	@echo "Running mypy..."
	mypy tai/ --ignore-missing-imports

format:
	@echo "Formatting with black..."
	black tai/
	@echo "Sorting imports with isort..."
	isort tai/

check: lint test
	@echo "All checks passed!"

# Build & Deploy
clean:
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type d -name .pytest_cache -exec rm -rf {} +

clean-all: clean
	@echo "Cleaning all artifacts and caches..."
	rm -rf .mypy_cache/
	rm -rf .tox/
	rm -rf .cache/
	rm -rf *.log
	find . -name "*.pyc" -delete
	find . -name "*.pyo" -delete
	find . -name "*.pyd" -delete

build: clean
	@echo "Building distribution packages..."
	python -m build

publish: build
	@echo "Publishing to PyPI..."
	twine upload dist/*

# Development
docs:
	@echo "Documentation generation not yet implemented"
	@echo "Consider using Sphinx or MkDocs for documentation"

# Quick development cycle
dev: format lint test
	@echo "Development cycle complete!"
