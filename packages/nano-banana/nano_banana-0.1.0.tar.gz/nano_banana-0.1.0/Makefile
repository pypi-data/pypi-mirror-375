# Nano Banana Package - UV 极速工作流 🍌⚡
# 基于 Gemini 2.5 Flash Image 的图像生成和分析包

.PHONY: sync test build publish clean dev format lint check release

# 🚀 初始化项目 (仅需运行一次)
init:
	@echo "🎉 使用 uv 初始化 nano-banana 项目..."
	uv sync
	@echo "✅ 项目初始化完成！"

# 📦 同步依赖 (超快速度)
sync:
	@echo "⚡ 同步依赖..."
	uv sync

# 🧪 运行测试 (UV 环境)
test:
	@echo "🧪 运行 nano-banana 测试..."
	uv run python tests/simple_test.py
	uv run python tests/quick_test.py
	uv run python tests/nano_banana_test.py
	@echo "🧪 运行 pytest..."
	uv run pytest tests/ -v

# 🚀 开发模式测试
dev:
	@echo "🚀 开发模式测试..."
	uv run python -c "import nano_banana as nb; print('✅ 导入成功')"
	uv run python -c "from nano_banana import NanoBanana; client = NanoBanana(); print('✅ 客户端创建成功')"
	@echo "💡 提示：请确保已设置 SIMEN_AI_API_KEY 或 OPENAI_API_KEY 环境变量"

# 🔨 构建包 (UV 原生构建)
build:
	@echo "🔨 使用 uv 构建 nano-banana 包..."
	uv build

# 🧪 发布到 TestPyPI (UV 原生)
test-publish:
	@echo "🧪 发布到 TestPyPI..."
	@echo "💡 需要设置环境变量: export UV_PUBLISH_TOKEN=your-testpypi-token"
	uv publish --token $$UV_PUBLISH_TOKEN --repository testpypi

# 🚀 发布到 PyPI (UV 原生)
publish:
	@echo "🚀 发布到 PyPI..."
	@echo "💡 需要设置环境变量: export UV_PUBLISH_TOKEN=your-pypi-token"
	uv publish --token $$UV_PUBLISH_TOKEN

# 🏢 发布到私有仓库
publish-private:
	@echo "🏢 发布到私有仓库..."
	uv publish --repository-url http://your-private-pypi.com/simple/

# 🧹 清理构建文件
clean:
	@echo "🧹 清理构建文件..."
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .uv_cache/
	find . -type d -name __pycache__ -delete
	find . -type f -name "*.pyc" -delete

# 📊 代码质量检查
lint:
	@echo "📊 代码质量检查..."
	uv run ruff check src/
	uv run mypy src/nano_banana/

# 🎨 代码格式化
format:
	@echo "🎨 代码格式化..."
	uv run ruff format src/

# ✅ 完整检查
check: lint test
	@echo "✅ 所有检查通过！"

# 🎉 完整发布流程 (极速版)
release: clean check build test-publish
	@echo "🎉 版本发布完成! 检查 TestPyPI 后运行 'make publish' 发布到正式 PyPI"

# ⚡ 添加依赖 (示例)
add-dep:
	@echo "示例: uv add openai"
	@echo "示例: uv add --dev pytest"
	@echo "示例: uv add --dev ruff"

# 🔄 更新所有依赖
update:
	@echo "🔄 更新所有依赖..."
	uv sync --upgrade

# 📋 显示依赖树
tree:
	@echo "📋 依赖树..."
	uv tree

# 🎯 快速开始 (新开发者)
quickstart: init test dev
	@echo "🎯 快速开始完成！可以开始开发了"

# 📄 运行示例脚本
examples:
	@echo "🎯 运行 nano-banana 示例..."
	@echo "1️⃣ 文本生成图片测试:"
	uv run tests/text_to_image_test.py
	@echo "\n2️⃣ 图片到图片测试:"
	uv run tests/image_to_image_test.py
	@echo "\n3️⃣ 图片分析测试:"
	uv run tests/simple_test.py

# 🔧 设置发布认证
setup-auth:
	@echo "🔧 设置发布认证..."
	@echo "1. 获取 PyPI API Token: https://pypi.org/manage/account/token/"
	@echo "2. 获取 TestPyPI API Token: https://test.pypi.org/manage/account/token/"
	@echo "3. 设置环境变量:"
	@echo "   export UV_PUBLISH_TOKEN=your-pypi-token"
	@echo "4. 然后运行: make test-publish 或 make publish"

# 🍌 nano-banana 专用命令

# 🎨 测试文本生成图片
test-text2img:
	@echo "🎨 测试文本生成图片功能..."
	uv run python -c "import nano_banana as nb; result = nb.text_to_image('一只可爱的橙色小猫'); print('生成结果:', result[:100] + '...')"

# 🔍 测试图片分析
test-analyze:
	@echo "🔍 测试图片分析功能..."
	uv run python tests/simple_test.py

# 🔄 测试图片到图片
test-img2img:
	@echo "🔄 测试图片到图片功能..."
	uv run python tests/image_to_image_test.py

# 🌐 检查环境变量
check-env:
	@echo "🌐 检查环境变量配置..."
	@if [ -z "$$SIMEN_AI_API_KEY" ] && [ -z "$$OPENAI_API_KEY" ]; then \
		echo "❌ 未设置 API 密钥！"; \
		echo "请设置以下环境变量之一:"; \
		echo "  export SIMEN_AI_API_KEY=your-simen-key"; \
		echo "  export OPENAI_API_KEY=your-openai-key"; \
	else \
		echo "✅ API 密钥已配置"; \
	fi
	@if [ -n "$$SIMEN_BASEURL" ]; then \
		echo "✅ SIMEN_BASEURL: $$SIMEN_BASEURL"; \
	else \
		echo "💡 可选：设置 SIMEN_BASEURL=https://api.simen.ai/v1"; \
	fi

# 🎉 完整功能测试
test-all: check-env test-text2img test-analyze test-img2img
	@echo "🎉 所有功能测试完成！"

# 📚 显示帮助信息
help:
	@echo "🍌 Nano Banana Makefile 命令帮助"
	@echo ""
	@echo "📦 项目管理:"
	@echo "  init          - 初始化项目"
	@echo "  sync          - 同步依赖"
	@echo "  clean         - 清理构建文件"
	@echo ""
	@echo "🧪 开发测试:"
	@echo "  dev           - 开发模式测试"
	@echo "  test          - 运行所有测试"
	@echo "  check-env     - 检查环境变量"
	@echo "  test-all      - 完整功能测试"
	@echo ""
	@echo "🍌 nano-banana 专用:"
	@echo "  test-text2img - 测试文本生成图片"
	@echo "  test-analyze  - 测试图片分析"
	@echo "  test-img2img  - 测试图片到图片"
	@echo ""
	@echo "🔨 构建发布:"
	@echo "  build         - 构建包"
	@echo "  test-publish  - 发布到 TestPyPI"
	@echo "  publish       - 发布到 PyPI"
	@echo "  release       - 完整发布流程"
	@echo ""
	@echo "💡 使用示例："
	@echo "  make quickstart  # 快速开始"
	@echo "  make test-all    # 测试所有功能"
	@echo "  make release     # 发布新版本"
