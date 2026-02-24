.PHONY: build install clean format format-html help

# Default output directory (current directory for local development)
OUTPUT_DIRECTORY ?= .

help:
	@echo "Available commands:"
	@echo "  install      Install dependencies using uv"
	@echo "  build        Generate and format the static site to the $(OUTPUT_DIRECTORY) directory"
	@echo "  clean        Remove the $(OUTPUT_DIRECTORY) directory"
	@echo "  format       Format Python code using black"
	@echo "  format-html  Format HTML files using prettier"

install:
	uv sync

build:
	uv run generate.py all --output-directory $(OUTPUT_DIRECTORY)
	npx prettier --write "$(OUTPUT_DIRECTORY)/**/*.html" "$(OUTPUT_DIRECTORY)/*.html"

clean:
	rm -rf $(OUTPUT_DIRECTORY)

format:
	uv run black .
	npx prettier --write "**/*.html"
