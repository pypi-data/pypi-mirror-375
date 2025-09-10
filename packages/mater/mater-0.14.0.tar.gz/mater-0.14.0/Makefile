.PHONY: help docs

# Default target - auto-generate help from comments
help: ## Show available commands
	@echo "📋 Available commands:"
	@grep -E '^[a-zA-Z_-]+:.*##' $(MAKEFILE_LIST) | awk 'BEGIN {FS = ":.*##"}; {printf "  make %-10s - %s\n", $$1, $$2}'


docs: ## Start live documentation server with auto-reload
	@echo "🚀 Starting live documentation server..."
	@echo ""
	uv sync --group docs
	@echo ""
	@echo "🔄 Watching for changes and auto-reloading..."
	@echo "   📍 Server: http://localhost:8000"
	@echo "   ⏹️  Stop: Ctrl+C"
	@echo ""
	(cd docs/source && uv run sphinx-autobuild . build/html --host 0.0.0.0 --port 8000)