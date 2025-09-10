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
	@if [ ! -f ~/.pypirc ]; then \
		echo "$(RED)❌ ~/.pypirc file not found$(NC)"; \
		echo "$(BLUE)Please create ~/.pypirc file with your tokens$(NC)"; \
		exit 1; \
	fi
	$(UV) run twine upload --repository testpypi $(BUILD_DIR)/*
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
	@if [ ! -f ~/.pypirc ]; then \
		echo "$(RED)❌ ~/.pypirc file not found$(NC)"; \
		echo "$(BLUE)Please create ~/.pypirc file with your tokens$(NC)"; \
		exit 1; \
	fi
	$(UV) run twine upload $(BUILD_DIR)/*
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
