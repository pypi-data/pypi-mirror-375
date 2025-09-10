# 📦 PyPI 发布指南

本文档提供了将 `tidevice3` 发布到 PyPI 的完整指南。

## 🔧 环境准备

### 1. 安装 uv (如果还没有)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
# 或
pip install uv
```

### 2. 注册 PyPI 账户
1. 访问 [PyPI](https://pypi.org/) 注册账户
2. 访问 [TestPyPI](https://test.pypi.org/) 注册测试账户（推荐）

### 3. 创建 API Token

#### 对于 PyPI (生产环境):
1. 登录 [PyPI](https://pypi.org/)
2. 前往 Account Settings → API tokens
3. 点击 "Add API token"
4. 选择 "Entire account" 或特定项目
5. 复制生成的 token (格式: `pypi-...`)

#### 对于 TestPyPI (测试环境):
1. 登录 [TestPyPI](https://test.pypi.org/)
2. 重复上述步骤

### 4. 配置 uv 认证

创建或编辑 `~/.netrc` 文件:
```bash
# 对于 PyPI
machine upload.pypi.org
login __token__
password pypi-YOUR_ACTUAL_TOKEN_HERE

# 对于 TestPyPI  
machine test.pypi.org
login __token__
password pypi-YOUR_ACTUAL_TESTPYPI_TOKEN_HERE
```

或者使用环境变量:
```bash
export UV_PUBLISH_TOKEN="pypi-YOUR_TOKEN_HERE"
export UV_PUBLISH_URL="https://upload.pypi.org/legacy/"  # 生产环境
# export UV_PUBLISH_URL="https://test.pypi.org/legacy/"  # 测试环境
```

## 🚀 发布流程

### 方法一：使用 Make 构建系统 (强烈推荐)

我们提供了专业的 `Makefile` 来管理整个构建和发布流程：

#### 1. 查看可用命令
```bash
make help
```

#### 2. 快速构建
```bash
make build
```

#### 3. 测试发布 (推荐先测试)
```bash
make publish-test
```

#### 4. 验证测试包
```bash
pip install --index-url https://test.pypi.org/simple/ tidevice3
t3 --help
```

#### 5. 正式发布
```bash
make publish
```

#### 6. 一键完整流程 (最安全)
```bash
make publish-all  # 测试→检查→TestPyPI→确认→PyPI
```

📖 **详细的 Make 使用指南请参考：[MAKE.md](MAKE.md)**

### 方法二：手动命令 (备用)

#### 1. 清理和构建
```bash
# 清理旧文件
rm -rf dist/ build/ *.egg-info/

# 同步依赖
uv sync

# 构建包
uv build
```

#### 2. 发布到 TestPyPI
```bash
uv publish --repository testpypi dist/*
```

#### 3. 发布到 PyPI
```bash
uv publish dist/*
```

## 📋 发布前检查清单

### ✅ 代码质量
- [ ] 所有测试通过: `uv run pytest`
- [ ] 代码格式正确: `uv run isort . && uv run black .`
- [ ] 没有明显的 linting 错误

### ✅ 版本管理
- [ ] 更新 `pyproject.toml` 中的版本号
- [ ] 更新 `README.md` (如果需要)
- [ ] 提交所有更改: `git add . && git commit -m "Release vX.X.X"`

### ✅ 包配置
- [ ] 检查 `pyproject.toml` 中的元数据
- [ ] 确认依赖版本正确
- [ ] 检查分类器 (classifiers) 准确

### ✅ 发布设置  
- [ ] PyPI 账户已创建
- [ ] API tokens 已配置
- [ ] 测试环境验证通过

## 🔄 版本管理策略

使用语义化版本 (Semantic Versioning):
- `MAJOR.MINOR.PATCH`
- `1.0.0` - 首个稳定版本
- `1.0.1` - 补丁修复
- `1.1.0` - 新功能
- `2.0.0` - 破坏性更改

更新版本号:
```bash
# 编辑 pyproject.toml
version = "0.1.2"  # 更新这里

# 创建 git tag
git tag v0.1.2
git push origin --tags
```

## 🎯 发布后操作

### 1. 验证发布
```bash
# 检查包是否可用
pip install tidevice3
t3 --help
```

### 2. 创建 GitHub Release
1. 前往 GitHub repository
2. 点击 "Releases"
3. 点击 "Create a new release"
4. 选择刚创建的 tag
5. 添加发布说明

### 3. 推广包
- 更新项目 README
- 在相关社区分享
- 考虑写博客介绍功能

## 🐛 常见问题

### 包名已存在
如果 `tidevice3` 名称已被占用，需要:
1. 修改 `pyproject.toml` 中的 `name` 字段
2. 更新所有相关脚本和文档

### 上传失败
- 检查 API token 是否正确
- 确认包名没有冲突
- 验证版本号没有重复

### 依赖问题
- 检查所有依赖是否在 PyPI 上可用
- 确认版本约束合理
- 测试在干净环境中的安装

## 📚 相关链接

- [PyPI](https://pypi.org/)
- [TestPyPI](https://test.pypi.org/) 
- [uv 文档](https://docs.astral.sh/uv/)
- [Python 打包指南](https://packaging.python.org/)
- [语义化版本](https://semver.org/)
