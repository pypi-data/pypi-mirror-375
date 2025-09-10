# Makefile for tidevice3 PyPI package management
# 
# This is a modular Makefile that includes separate files for different concerns:
# - variables.mk: Project variables and configuration
# - development.mk: Development workflow targets
# - build.mk: Package building targets
# - publish.mk: Publishing targets
# - utils.mk: Utility and information targets
#
# Usage: make <target>
# Run 'make help' for available targets

# Include all module files
include makefiles/variables.mk
include makefiles/development.mk
include makefiles/build.mk
include makefiles/publish.mk
include makefiles/utils.mk

# Default target
.DEFAULT_GOAL := help

.PHONY: help

# Help target - displays available targets
help: ## Show this help message
	@echo "$(BLUE)$(PACKAGE_NAME) Modular Build System$(NC)"
	@echo ""
	@echo "$(GREEN)Available targets:$(NC)"
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  $(YELLOW)%-15s$(NC) %s\n", $$1, $$2}' $(MAKEFILE_LIST)
	@echo ""
	@echo "$(GREEN)Examples:$(NC)"
	@echo "  make clean build     # Clean and build package"
	@echo "  make test lint       # Run tests and linting"
	@echo "  make publish-test    # Build and publish to TestPyPI"
	@echo "  make publish-all     # Full workflow: test → TestPyPI → PyPI"
	@echo ""
	@echo "$(BLUE)📁 For module structure info: make help-modules$(NC)"
