.PHONY: build install clean format format-html help

# Default output directory (current directory for local development)
OUTPUT_DIRECTORY ?= .

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies using uv"
	@echo "  build        Generate and format the static site to the $(OUTPUT_DIRECTORY) directory"
	@echo "  clean        Surgically remove build artifacts and cache files (safely handles '.')"
	@echo "  format       Format Python code using black"
	@echo "  format-html  Format HTML files using prettier"

# Use copy mode for links to support NTFS drives in WSL
UV_LINK_MODE ?= copy
# Fallback environment path for WSL/NTFS issues
HOME_VENV_DIR := $(HOME)/.venv
HOME_VENV := $(HOME_VENV_DIR)/food-log

# Helper to find which environment to use
# 1. Check if .venv is a VALID environment (has a bin/python)
# 2. Otherwise check if home venv is a VALID environment
VENV_PATH := $(shell \
	if [ -x ".venv/bin/python" ]; then echo ".venv"; \
	elif [ -x "$(HOME_VENV)/bin/python" ]; then echo "$(HOME_VENV)"; \
	else echo ".venv"; fi)
UV_ENV_FLAG := UV_PROJECT_ENVIRONMENT=$(VENV_PATH)

install:
	@echo "Installing dependencies..."
	@if ! uv sync --link-mode $(UV_LINK_MODE); then \
		echo "NTFS/WSL detected, falling back to $(HOME_VENV)..."; \
		mkdir -p $(HOME_VENV_DIR); \
		rm -rf $(HOME_VENV); \
		uv venv $(HOME_VENV); \
		UV_PROJECT_ENVIRONMENT=$(HOME_VENV) uv sync --link-mode $(UV_LINK_MODE); \
	fi

build:
	@echo "Generating and formatting site..."
	@$(UV_ENV_FLAG) uv run --link-mode $(UV_LINK_MODE) generate.py all --output-directory $(OUTPUT_DIRECTORY)
	npx prettier --write --ignore-path /dev/null "$(OUTPUT_DIRECTORY)/*.html" "$(OUTPUT_DIRECTORY)/logs/**/*.html"

clean:
	@if [ "$(OUTPUT_DIRECTORY)" = "." ] || [ "$(OUTPUT_DIRECTORY)" = "./" ]; then \
		echo "Cleaning build artifacts and cache..."; \
		rm -f index.html food_database.html history.html; \
		find logs -maxdepth 1 -name "*.html" -type f -delete 2>/dev/null || true; \
		find logs -name "*.html" -type f -delete 2>/dev/null || true; \
		find . -type d -name "__pycache__" -exec rm -rf {} +; \
		rm -rf dist/ .pytest_cache .ruff_cache .uv/; \
	else \
		echo "Cleaning $(OUTPUT_DIRECTORY)..."; \
		rm -rf $(OUTPUT_DIRECTORY); \
	fi

format:
	@$(UV_ENV_FLAG) uv run --link-mode $(UV_LINK_MODE) black .
	npx prettier --write --ignore-path /dev/null "**/*.html" || true
