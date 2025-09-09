.PHONY: help install install-dev test lint format clean build

help: ## 显示帮助信息
	@echo "可用的命令:"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}'

install: ## 安装依赖
	pip install -e .

install-dev: ## 安装开发依赖
	pip install -e ".[dev]"

test: ## 运行测试
	pytest tests/ -v

lint: ## 运行代码检查
	ruff check src/ tests/ examples/
	mypy src/

format: ## 格式化代码
	ruff format src/ tests/ examples/

clean: ## 清理构建文件
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete

build: clean ## 构建包
	python -m build

install-build: build ## 构建并安装
	pip install dist/*.whl
