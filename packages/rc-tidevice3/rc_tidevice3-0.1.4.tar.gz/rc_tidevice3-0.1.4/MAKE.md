# 🔨 Make 模块化构建系统使用指南

本项目使用**模块化 Makefile** 来管理构建、测试和发布流程，提供统一、简洁且易于维护的命令接口。

## 📁 模块化结构

项目采用模块化的 Makefile 组织方式，将不同功能分散到专门的文件中：

```
Makefile                  # 主入口文件
makefiles/
├── variables.mk         # 项目变量和配置
├── development.mk       # 开发工作流目标  
├── build.mk            # 包构建目标
├── publish.mk          # 发布目标
└── utils.mk            # 工具和信息目标
```

### 🎯 模块化的优势

- ✅ **更好的组织**: 每个文件专注于特定功能
- ✅ **易于维护**: 修改特定功能时只需编辑对应文件
- ✅ **可重用性**: 模块可以在其他项目中复用
- ✅ **清晰的关注点分离**: 开发、构建、发布各自独立
- ✅ **更容易协作**: 团队成员可以专注于特定模块

## 🚀 快速开始

```bash
# 查看所有可用命令
make help

# 查看模块化结构信息
make help-modules

# 开发环境设置
make dev

# 运行测试和检查
make test lint

# 构建包
make build

# 发布到 TestPyPI
make publish-test

# 发布到 PyPI
make publish
```

## 📋 完整命令列表

### 🛠️ 开发相关

| 命令 | 描述 |
|------|------|
| `make help` | 显示帮助信息 |
| `make install` | 安装包和依赖 |
| `make dev` | 安装开发依赖 |
| `make clean` | 清理构建产物和缓存 |

### 🧪 测试和质量检查

| 命令 | 描述 |
|------|------|
| `make test` | 运行测试套件 |
| `make lint` | 运行代码检查 |
| `make format` | 格式化代码 |
| `make dev-workflow` | 开发工作流：格式化→测试→检查 |

### 📦 构建和发布

| 命令 | 描述 |
|------|------|
| `make build` | 构建发布包 |
| `make validate` | 验证包的完整性 |
| `make publish-test` | 发布到 TestPyPI |
| `make publish` | 发布到 PyPI（生产环境）|
| `make publish-all` | 完整发布流程 |
| `make release-prep` | 发布前准备 |

### ℹ️ 信息查看

| 命令 | 描述 |
|------|------|
| `make info` | 显示包详细信息 |
| `make check-version` | 显示当前版本 |
| `make stats` | 显示项目统计信息 |

## 🔄 典型工作流程

### 日常开发

```bash
# 1. 设置开发环境
make dev

# 2. 开发代码...

# 3. 开发工作流检查
make dev-workflow

# 4. 提交代码
git add .
git commit -m "Your changes"
```

### 发布新版本

```bash
# 1. 更新版本号
# 编辑 pyproject.toml 中的 version 字段

# 2. 发布前完整检查
make release-prep

# 3. 测试发布
make publish-test

# 4. 验证 TestPyPI 上的包
pip install --index-url https://test.pypi.org/simple/ tidevice3
t3 --help

# 5. 正式发布
make publish

# 6. 创建 Git tag
git tag v$(grep '^version' pyproject.toml | cut -d'"' -f2)
git push origin --tags
```

### 完整自动化发布

```bash
# 一键完成：测试→检查→TestPyPI→确认→PyPI
make publish-all
```

## 🎯 常用组合命令

```bash
# 清理重建
make clean build

# 完整测试
make test lint

# 发布前检查
make clean test lint build validate

# 查看包信息
make info stats
```

## 🔧 自定义配置

你可以通过环境变量自定义行为：

```bash
# 使用不同的 Python 版本
PYTHON=python3.11 make test

# 使用不同的 uv 命令
UV=/path/to/uv make build

# 设置包名（如果需要）
PACKAGE_NAME=my-package make info
```

## 🐛 故障排除

### 构建失败
```bash
# 清理后重试
make clean
make build
```

### 测试失败
```bash
# 查看详细测试输出
make test

# 检查代码格式
make format
make lint
```

### 发布失败
```bash
# 验证包完整性
make validate

# 检查认证配置
cat ~/.netrc

# 验证版本号
make check-version
```

## 📚 相关文件

- `Makefile` - 构建系统定义
- `pyproject.toml` - 项目配置
- `PUBLISH.md` - 详细发布指南
- `README.md` - 项目说明

## 🔧 自定义和扩展

### 添加新的模块

1. 在 `makefiles/` 目录下创建新的 `.mk` 文件
2. 在主 `Makefile` 中添加 `include` 声明
3. 确保使用正确的变量引用

示例：创建 `makefiles/docker.mk`
```makefile
# docker.mk - Docker 相关目标
.PHONY: docker-build docker-run

docker-build: ## Build Docker image
	@echo "$(YELLOW)🐳 Building Docker image...$(NC)"
	docker build -t $(PACKAGE_NAME):$(VERSION) .
```

然后在主 `Makefile` 中添加：
```makefile
include makefiles/docker.mk
```

### 自定义变量

在 `makefiles/variables.mk` 中修改或添加变量：
```makefile
# 自定义 Python 版本
PYTHON := python3.11

# 添加新的目录
DOCS_DIR := docs

# 自定义颜色
PURPLE := \033[0;35m
```

### 项目特定的目标

在对应的模块文件中添加项目特定的目标：
```makefile
# 在 development.mk 中添加
docs: ## Generate documentation
	@echo "$(YELLOW)📖 Generating documentation...$(NC)"
	$(UV) run sphinx-build -b html $(DOCS_DIR) $(BUILD_DIR)/docs
```

## 💡 提示

1. **使用 Tab 补全**: `make` 命令支持 Tab 补全目标名称
2. **并行执行**: 可以组合多个目标：`make clean build test`
3. **查看执行过程**: 所有命令都有彩色输出和进度提示
4. **安全发布**: `make publish` 会要求确认才发布到生产环境
5. **完整工作流**: `make publish-all` 提供最安全的发布流程
6. **模块化管理**: 使用 `make help-modules` 了解文件结构
7. **变量重用**: 所有模块共享 `variables.mk` 中的变量

使用 `make help` 随时查看最新的可用命令！
