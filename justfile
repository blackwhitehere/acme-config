# acme-config
# Run `just --list` to see available commands

# Default recipe
default:
    @just --list

# Run all tests
test:
    uv run pytest tests/ -v

# Lint code
lint:
    uv run ruff check src/ tests/

# Format code
format:
    uv run ruff format src/ tests/

# Fix linting issues
fix:
    uv run ruff check src/ tests/ --fix

# Install dependencies
install:
    uv sync

# Clean generated files
clean:
    rm -rf .pytest_cache __pycache__ .ruff_cache
    find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
    find . -type f -name "*.pyc" -delete 2>/dev/null || true
