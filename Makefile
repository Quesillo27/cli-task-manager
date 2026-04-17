.PHONY: help install install-dev test lint format clean run-demo docker-build docker-run

help:
	@echo "CLI Task Manager - Development Commands"
	@echo ""
	@echo "Installation:"
	@echo "  make install          Install dependencies"
	@echo "  make install-dev      Install dependencies + dev tools"
	@echo ""
	@echo "Development:"
	@echo "  make lint             Check code style"
	@echo "  make format           Format code with black"
	@echo "  make test             Run unit tests"
	@echo "  make test-verbose     Run tests with verbose output"
	@echo "  make test-coverage    Run tests with coverage report"
	@echo ""
	@echo "Running:"
	@echo "  make run-demo         Run demo scenario"
	@echo "  make clean-db         Delete task database"
	@echo ""
	@echo "Docker:"
	@echo "  make docker-build     Build Docker image"
	@echo "  make docker-run       Run Docker container"
	@echo ""
	@echo "Cleanup:"
	@echo "  make clean            Remove build artifacts and cache"

install:
	pip install -r requirements.txt

install-dev:
	pip install -r requirements.txt
	pip install pytest pytest-cov black flake8 mypy

test:
	python -m pytest tests/ -q

test-verbose:
	python -m pytest tests/ -v

test-coverage:
	python -m pytest tests/ --cov=task_manager --cov-report=html --cov-report=term
	@echo "Coverage report generated in htmlcov/index.html"

lint:
	flake8 task_manager tests main.py

format:
	black task_manager tests main.py

type-check:
	mypy task_manager --ignore-missing-imports

clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	rm -rf build/ dist/ htmlcov/ .pytest_cache/ .coverage
	@echo "Cleaned up build artifacts"

clean-db:
	rm -f ~/.task-manager/tasks.db
	@echo "Database cleared"

run-demo:
	@echo "Running demo scenario..."
	python main.py add "Demo Task 1" --project "Demo" --priority high --due "2026-04-01"
	python main.py add "Demo Task 2" --project "Demo" --priority medium
	python main.py add "Demo Task 3" --project "General"
	python main.py list
	@echo "Demo complete!"

docker-build:
	docker build -t cli-task-manager:latest .
	@echo "Docker image built successfully"

docker-run:
	docker run --rm cli-task-manager:latest list

docker-shell:
	docker run --rm -it cli-task-manager:latest bash

.DEFAULT_GOAL := help
