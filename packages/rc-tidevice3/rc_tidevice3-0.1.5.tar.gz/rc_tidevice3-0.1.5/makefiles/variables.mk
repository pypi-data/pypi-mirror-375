# variables.mk - 项目变量定义
# This file contains all project-specific variables

# Package information
PACKAGE_NAME := tidevice3
PYTHON := python3
UV := uv

# Directories
BUILD_DIR := dist
TEST_DIR := tests
SRC_DIR := tidevice3

# Colors for output
GREEN := \033[0;32m
YELLOW := \033[0;33m
RED := \033[0;31m
BLUE := \033[0;34m
NC := \033[0m # No Color

# Version extraction
VERSION := $(shell grep '^version' pyproject.toml | cut -d'"' -f2)

# Build artifacts
WHEEL_FILE := $(BUILD_DIR)/$(PACKAGE_NAME)-$(VERSION)-py3-none-any.whl
SDIST_FILE := $(BUILD_DIR)/$(PACKAGE_NAME)-$(VERSION).tar.gz
