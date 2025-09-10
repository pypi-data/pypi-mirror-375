# development.mk - 开发相关的目标
# This file contains targets for development workflow

.PHONY: install dev clean test lint format dev-workflow

# Install package and dependencies
install: ## Install package and dependencies
	@echo "$(YELLOW)📦 Installing package and dependencies...$(NC)"
	$(UV) sync
	@echo "$(GREEN)✅ Installation completed$(NC)"

# Install development dependencies
dev: install ## Install with development dependencies
	@echo "$(YELLOW)🛠️ Installing development dependencies...$(NC)"
	$(UV) sync --group dev
	@echo "$(GREEN)✅ Development setup completed$(NC)"

# Clean build artifacts
clean: ## Clean build artifacts and cache
	@echo "$(YELLOW)🧹 Cleaning build artifacts...$(NC)"
	rm -rf $(BUILD_DIR)/ build/ *.egg-info/
	rm -rf .pytest_cache/ .coverage htmlcov/
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	@echo "$(GREEN)✅ Clean completed$(NC)"

# Run tests
test: ## Run tests with pytest
	@echo "$(YELLOW)🧪 Running tests...$(NC)"
	$(UV) run pytest $(TEST_DIR)/ -v --cov=$(PACKAGE_NAME) --cov-report=term-missing
	@echo "$(GREEN)✅ Tests completed$(NC)"

# Run linting
lint: ## Run code linting and formatting checks
	@echo "$(YELLOW)🔍 Running linting checks...$(NC)"
	$(UV) run isort --check-only --diff .
	@echo "$(GREEN)✅ Linting completed$(NC)"

# Format code
format: ## Format code with isort
	@echo "$(YELLOW)📝 Formatting code...$(NC)"
	$(UV) run isort .
	@echo "$(GREEN)✅ Code formatting completed$(NC)"

# Quick development workflow
dev-workflow: format test lint ## Quick development workflow: format → test → lint
	@echo "$(GREEN)🔄 Development workflow completed$(NC)"
