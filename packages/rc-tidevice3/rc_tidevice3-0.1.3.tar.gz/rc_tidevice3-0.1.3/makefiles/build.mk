# build.mk - 构建相关的目标
# This file contains targets for building packages

.PHONY: build validate pre-build check-build

# Pre-build checks
pre-build:
	@echo "$(BLUE)🔍 Pre-build checks...$(NC)"
	@if [ ! -f "pyproject.toml" ]; then \
		echo "$(RED)❌ pyproject.toml not found$(NC)"; \
		exit 1; \
	fi
	@echo "$(GREEN)✅ Pre-build checks passed$(NC)"

# Build package
build: clean pre-build ## Build package for distribution
	@echo "$(YELLOW)🏗️ Building package...$(NC)"
	$(UV) build
	@echo "$(GREEN)✅ Build completed$(NC)"
	@echo "$(BLUE)📁 Built files:$(NC)"
	@ls -la $(BUILD_DIR)/

# Validate package before publishing
validate: build ## Validate package before publishing
	@echo "$(YELLOW)🔍 Validating package...$(NC)"
	$(UV) run twine check $(BUILD_DIR)/*
	@echo "$(GREEN)✅ Package validation completed$(NC)"

# Check if build artifacts exist
check-build:
	@if [ ! -d "$(BUILD_DIR)" ]; then \
		echo "$(RED)❌ $(BUILD_DIR)/ directory not found. Run 'make build' first.$(NC)"; \
		exit 1; \
	fi
	@if [ -z "$$(ls -A $(BUILD_DIR)/)" ]; then \
		echo "$(RED)❌ No files found in $(BUILD_DIR)/. Run 'make build' first.$(NC)"; \
		exit 1; \
	fi

# Release preparation
release-prep: clean test lint build validate ## Prepare for release: clean → test → lint → build → validate
	@echo "$(GREEN)🚀 Release preparation completed$(NC)"
	@echo "$(BLUE)📋 Next steps:$(NC)"
	@echo "  1. make publish-test  # Test on TestPyPI"
	@echo "  2. make publish       # Publish to PyPI"
	@echo "  3. git tag v$(VERSION)"
	@echo "  4. git push origin --tags"
