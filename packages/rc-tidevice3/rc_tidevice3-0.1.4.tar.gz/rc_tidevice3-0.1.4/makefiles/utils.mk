# utils.mk - 工具和信息相关的目标
# This file contains utility targets and information display

.PHONY: check-version info stats help-modules

# Check package version
check-version: ## Display current package version
	@echo "$(BLUE)📋 Package Information:$(NC)"
	@echo "Package: $(PACKAGE_NAME)"
	@echo "Version: $(VERSION)"
	@echo ""

# Show package info
info: check-version ## Show detailed package information
	@echo "$(BLUE)🔍 Dependencies:$(NC)"
	@grep -A 20 "^dependencies" pyproject.toml
	@echo ""
	@echo "$(BLUE)📊 Package size:$(NC)"
	@if [ -d "$(BUILD_DIR)" ]; then du -h $(BUILD_DIR)/*; else echo "No built packages found. Run 'make build' first."; fi

# Show project statistics
stats: ## Show project statistics
	@echo "$(BLUE)📊 Project Statistics:$(NC)"
	@echo "Lines of code:"
	@find $(SRC_DIR)/ -name "*.py" | xargs wc -l | tail -1
	@echo ""
	@echo "Test files:"
	@find $(TEST_DIR)/ -name "*.py" | wc -l | xargs echo "Test files:"
	@echo ""
	@echo "Dependencies:"
	@grep -c "^    " pyproject.toml || echo "0"

# Show information about modular Makefile structure
help-modules: ## Show information about Makefile modules
	@echo "$(BLUE)📁 Makefile Modules:$(NC)"
	@echo "  $(YELLOW)variables.mk$(NC)    - Project variables and configuration"
	@echo "  $(YELLOW)development.mk$(NC)  - Development workflow targets"
	@echo "  $(YELLOW)build.mk$(NC)        - Package building targets"
	@echo "  $(YELLOW)publish.mk$(NC)      - Publishing targets"
	@echo "  $(YELLOW)utils.mk$(NC)        - Utility and information targets"
	@echo ""
	@echo "$(GREEN)Benefits of modular structure:$(NC)"
	@echo "  ✅ Better organization and maintainability"
	@echo "  ✅ Easier to find and edit specific functionality"
	@echo "  ✅ Reusable across similar projects"
	@echo "  ✅ Clear separation of concerns"
