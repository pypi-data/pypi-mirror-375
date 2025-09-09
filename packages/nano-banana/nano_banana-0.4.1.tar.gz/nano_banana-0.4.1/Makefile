.PHONY: test build clean install publish test-publish

# 🧪 测试
test:
	uv run tests/simple_test.py

# 🔨 构建
build:
	uv build

# 🧹 清理
clean:
	rm -rf build/ dist/ *.egg-info/
	find . -type d -name __pycache__ -delete

# 📦 安装
install:
	uv sync

# 🧪 发布到 TestPyPI
test-publish: clean build
	uv publish --repository testpypi

# 🚀 发布到 PyPI
publish: clean build
	uv publish
