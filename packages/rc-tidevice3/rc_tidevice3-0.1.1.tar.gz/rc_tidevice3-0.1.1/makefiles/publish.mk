# publish.mk - 发布相关的目标
# This file contains targets for publishing packages

.PHONY: publish-test publish publish-all confirm-production

# Confirm production publish
confirm-production:
	@echo "$(RED)⚠️  You are about to publish to PRODUCTION PyPI!$(NC)"
	@echo "$(BLUE)📦 Package: $(PACKAGE_NAME)$(NC)"
	@echo "$(BLUE)📁 Files to upload:$(NC)"
	@ls -la $(BUILD_DIR)/
	@echo ""
	@read -p "Are you sure you want to continue? (y/N): " confirm && [ "$$confirm" = "y" ]

# Publish to TestPyPI
publish-test: build check-build ## Build and publish to TestPyPI
	@echo "$(YELLOW)🚀 Publishing to TestPyPI...$(NC)"
	@if [ -z "$$TESTPYPI_TOKEN" ]; then \
		echo "$(RED)❌ TESTPYPI_TOKEN environment variable not set$(NC)"; \
		echo "$(BLUE)Please set your TestPyPI token:$(NC)"; \
		echo "  export TESTPYPI_TOKEN='pypi-YOUR_TESTPYPI_TOKEN_HERE'"; \
		exit 1; \
	fi
	$(UV) publish --publish-url https://test.pypi.org/legacy/ --token $$TESTPYPI_TOKEN $(BUILD_DIR)/*
	@echo "$(GREEN)🎉 Published to TestPyPI successfully!$(NC)"
	@echo ""
	@echo "$(BLUE)🧪 Test your package:$(NC)"
	@echo "  pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"
	@echo ""
	@echo "$(BLUE)🔗 View on TestPyPI:$(NC)"
	@echo "  https://test.pypi.org/project/$(PACKAGE_NAME)/"

# Publish to PyPI (production)
publish: build check-build confirm-production ## Build and publish to PyPI (production)
	@echo "$(YELLOW)📤 Publishing to PyPI...$(NC)"
	@if [ -z "$$PYPI_TOKEN" ]; then \
		echo "$(RED)❌ PYPI_TOKEN environment variable not set$(NC)"; \
		echo "$(BLUE)Please set your PyPI token:$(NC)"; \
		echo "  export PYPI_TOKEN='pypi-YOUR_PYPI_TOKEN_HERE'"; \
		exit 1; \
	fi
	$(UV) publish --publish-url https://upload.pypi.org/legacy/ --token $$PYPI_TOKEN $(BUILD_DIR)/*
	@echo "$(GREEN)🎉 Published to PyPI successfully!$(NC)"
	@echo ""
	@echo "$(BLUE)🔗 View on PyPI:$(NC)"
	@echo "  https://pypi.org/project/$(PACKAGE_NAME)/"
	@echo ""
	@echo "$(BLUE)📦 Install your package:$(NC)"
	@echo "  pip install $(PACKAGE_NAME)"

# Full workflow: test, build, publish to TestPyPI, then PyPI
publish-all: test lint validate publish-test ## Full workflow: test → lint → validate → TestPyPI → PyPI
	@echo ""
	@echo "$(GREEN)🎯 TestPyPI publication completed. Testing before production...$(NC)"
	@echo ""
	@echo "$(YELLOW)Please test the package from TestPyPI:$(NC)"
	@echo "  pip install --index-url https://test.pypi.org/simple/ $(PACKAGE_NAME)"
	@echo "  $(PACKAGE_NAME) --help"
	@echo ""
	@read -p "If testing is successful, continue to PyPI? (y/N): " confirm && [ "$$confirm" = "y" ]
	@$(MAKE) publish
