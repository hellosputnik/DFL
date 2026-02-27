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

install:
	uv sync

build:
	uv run generate.py all --output-directory $(OUTPUT_DIRECTORY)
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
	uv run black .
	npx prettier --write --ignore-path /dev/null "**/*.html" || true
