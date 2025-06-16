# Makefile for alletaal-lint development

.PHONY: help install install-dev test test-cov lint format type-check clean build upload docs serve-docs

# Default target
help:
	@echo "Available targets:"
	@echo "  install       Install package for regular use"
	@echo "  install-dev   Install package for development"
	@echo "  install-model Install Dutch spaCy model"
	@echo "  test          Run tests"
	@echo "  test-cov      Run tests with coverage"
	@echo "  lint          Run linting checks"
	@echo "  format        Format code with black and isort"
	@echo "  type-check    Run type checking with mypy"
	@echo "  clean         Clean build artifacts"
	@echo "  build         Build package"
	@echo "  server        Start development server"
	@echo "  docker-build  Build Docker image"
	@echo "  docker-up     Start with docker-compose"
	@echo "  docker-down   Stop docker-compose services"
	@echo "  example-cli   Run CLI examples"
	@echo "  example-api   Test API endpoints"
	@echo "  perf-test     Run performance tests"
	@echo "  ci-local      Run all CI checks locally"

# Installation targets
install:
	pip install -e .

install-dev:
	pip install -e ".[dev]"
	pre-commit install

install-model:
	python -m spacy download nl_core_news_sm

# Testing targets
test:
	pytest tests/ -v

test-cov:
	pytest tests/ --cov=alletaal_lint --cov-report=html --cov-report=term-missing

test-watch:
	pytest-watch tests/ --runner "pytest --cov=alletaal_lint"

# Code quality targets
lint:
	flake8 src/ tests/
	black --check src/ tests/
	isort --check-only src/ tests/

format:
	black src/ tests/
	isort src/ tests/

type-check:
	mypy src/alletaal_lint/

check: lint type-check test

# Development server
server:
	alletaal-lint server --reload

# Documentation
docs:
	@echo "Documentation is in README.md"
	@echo "API docs available at http://localhost:8000/docs when server is running"

# Build and distribution
clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .coverage
	rm -rf htmlcov/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean
	python -m build

upload-test: build
	python -m twine upload --repository testpypi dist/*

upload: build
	python -m twine upload dist/*

# Docker targets
docker-build:
	docker build -t alletaal-lint .

docker-run:
	docker run -d -p 8000:8000 --name alletaal-lint alletaal-lint

docker-stop:
	docker stop alletaal-lint && docker rm alletaal-lint

docker-logs:
	docker logs -f alletaal-lint

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

docker-health:
	curl -f http://localhost:8000/health || echo "Service not healthy"

# Example usage
example-cli:
	@echo "Running CLI examples..."
	alletaal-lint sentence "De kat zit op de mat."
	alletaal-lint score --text "Rijkswaterstaat werkt het hele jaar op de A9 tussen Badhoevedorp en Holendrecht en aan de Ring A10 Zuid , project Zuidasdok." --detailed
	@echo ""
	@echo "Note: Scores may differ from T-Scan due to modern NLP implementation differences."
	@echo "See METHODOLOGY.md for detailed comparison."

debug-sentence:
	@echo "Debugging specific sentence..."
	@python debug_sentence.py

example-api:
	@echo "Starting API server in background..."
	alletaal-lint server &
	@echo "Waiting for server to start..."
	sleep 3
	@echo "Testing API endpoint..."
	curl -X POST "http://localhost:8000/score-sentence" \
		-H "Content-Type: application/json" \
		-d '{"text": "Dit is een test zin voor de API."}'
	@echo "\nStopping server..."
	pkill -f "alletaal-lint server"

# Development utilities
dev-setup: install-dev install-model
	@echo "Development environment ready!"

ci-test: lint type-check test-cov
	@echo "All CI checks passed!"

ci-local: format lint type-check test-cov
	@echo "Running local CI simulation..."
	@echo "✓ Code formatting"
	@echo "✓ Linting" 
	@echo "✓ Type checking"
	@echo "✓ Tests with coverage"
	@echo "All local CI checks passed! Ready for GitHub Actions."

# Performance testing
perf-test:
	@echo "Running performance tests..."
	@python -c "\
import time; \
from alletaal_lint import Document; \
text = 'Dit is een test. ' * 1000; \
start = time.time(); \
doc = Document(text); \
score = doc.calculate_lint_score(); \
end = time.time(); \
print(f'Processed {len(text)} characters in {end-start:.3f} seconds'); \
print(f'Score: {score}'); \
"