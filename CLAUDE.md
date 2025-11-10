# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DeepAgents 是一个基于 LangGraph 构建的通用深度智能体框架，支持子智能体生成、任务列表管理和文件系统交互。该项目采用模块化的中间件架构，使智能体能够处理复杂的长期任务。

## 开发环境配置

### 环境要求
- Python >= 3.11
- uv (推荐的包管理器)

### 安装依赖
```bash
# 安装开发依赖
uv sync --all-groups

# 安装生产依赖
uv sync --group dev
```

## 常用开发命令

### 代码质量检查
```bash
# 格式化代码
make format

# 检查所有文件
make lint

# 检查变更的文件
make lint_diff

# 只检查包文件
make lint_package

# 只检查测试文件
make lint_tests
```

### 测试运行
```bash
# 运行单元测试
make test

# 运行集成测试
make integration_test

# 直接使用 pytest
uv run pytest libs/deepagents/tests/unit_tests --cov=deepagents --cov-report=term-missing
uv run pytest libs/deepagents/tests/integration_tests --cov=deepagents --cov-report=term-missing
```

### 类型检查
```bash
# 运行 mypy 类型检查
uv run --all-groups mypy libs/deepagents --cache-dir .mypy_cache
```

## 项目架构

### 核心组件
- **libs/deepagents/**: 主要的 Python 包
  - **graph.py**: 核心的 `create_deep_agent` 函数，用于创建深度智能体
  - **middleware/**: 模块化的中间件系统
    - **filesystem.py**: 文件系统中间件，提供文件读写工具
    - **subagents.py**: 子智能体中间件，支持上下文隔离
  - **backends/**: 支持不同的存储后端
  - **tests/**: 完整的测试套件（单元测试和集成测试）

- **libs/deepagents-cli/**: CLI 工具包
- **examples/**: 示例代码和用法

### 中间件架构
DeepAgents 采用可组合的中间件架构：
- **TodoListMiddleware**: 提供规划和任务分解功能
- **FilesystemMiddleware**: 提供文件系统交互工具
- **SubAgentMiddleware**: 支持子智能体生成和上下文隔离

## 关键特性

### 内置工具
深度智能体默认包含以下核心工具：
- **规划工具**: `write_todos` 用于任务分解和进度跟踪
- **文件系统工具**: `ls`, `read_file`, `write_file`, `edit_file`
- **子智能体工具**: `task` 用于生成专门的子智能体

### 默认配置
- 默认模型: `claude-sonnet-4-5-20250929`
- 最大令牌数: 20000
- 代码格式化: 使用 ruff (line-length: 150)
- 文档风格: Google 风格的 docstring

## 测试策略

### 测试组织
- **单元测试**: `libs/deepagents/tests/unit_tests/`
  - 测试各个中间件组件
  - 测试核心图功能
- **集成测试**: `libs/deepagents/tests/integration_tests/`
  - 测试完整的工作流
  - 测试与外部工具的集成

### 运行特定测试
```bash
# 运行特定测试文件
uv run pytest libs/deepagents/tests/unit_tests/test_middleware.py

# 运行特定测试函数
uv run pytest libs/deepagents/tests/unit_tests/test_middleware.py::test_function_name

# 运行带详细输出的测试
uv run pytest -v libs/deepagents/tests/unit_tests/
```

## 开发工作流

### 代码修改流程
1. 创建功能分支
2. 进行代码修改
3. 运行 `make lint` 检查代码质量
4. 运行 `make test` 确保测试通过
5. 运行 `make format` 格式化代码
6. 提交更改

### 调试技巧
- 使用 `uv run pytest -s` 运行测试并查看打印输出
- 使用 `uv run pytest --pdb` 在测试失败时进入调试器
- 集成测试可能需要外部 API 密钥（如 TAVILY_API_KEY）

## 重要配置文件

- **pyproject.toml**: 项目配置、依赖管理和工具配置
- **Makefile**: 常用开发任务的快捷命令
- **.github/workflows/**: CI/CD 配置
- **ruff**: 用于代码格式化和 linting
- **mypy**: 用于静态类型检查

## 构建和发布

项目使用标准的 Python 构建工具链：
```bash
# 构建包
uv run build

# 发布到 PyPI
uv run twine upload dist/*
```