#!/bin/bash
# 配置 PyPI 认证的辅助脚本

echo "🔐 PyPI 认证配置助手"
echo ""

# 检查 .netrc 文件是否存在
NETRC_FILE="$HOME/.netrc"

echo "1. 请输入你的 TestPyPI API Token (以 pypi- 开头):"
read -p "TestPyPI Token: " TESTPYPI_TOKEN

echo ""
echo "2. 请输入你的 PyPI API Token (以 pypi- 开头):"
read -p "PyPI Token: " PYPI_TOKEN

echo ""
echo "正在配置 ~/.netrc 文件..."

# 备份现有的 .netrc 文件
if [ -f "$NETRC_FILE" ]; then
    cp "$NETRC_FILE" "$NETRC_FILE.backup.$(date +%Y%m%d_%H%M%S)"
    echo "已备份现有的 .netrc 文件"
fi

# 创建新的 .netrc 文件
cat > "$NETRC_FILE" << EOF
# TestPyPI configuration
machine test.pypi.org
login __token__
password $TESTPYPI_TOKEN

# PyPI configuration  
machine upload.pypi.org
login __token__
password $PYPI_TOKEN
EOF

# 设置正确的权限
chmod 600 "$NETRC_FILE"

echo "✅ 认证配置完成！"
echo ""
echo "📁 配置文件位置: $NETRC_FILE"
echo "🔒 文件权限已设置为 600"
echo ""
echo "🚀 现在你可以使用以下命令发布:"
echo "  make publish-test  # 发布到 TestPyPI"
echo "  make publish       # 发布到 PyPI"
echo ""
echo "⚠️ 重要提醒:"
echo "  - 不要将 .netrc 文件提交到 git 仓库"
echo "  - Token 具有完整账户权限，请妥善保管"
