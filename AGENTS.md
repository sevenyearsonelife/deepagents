# Repository Guidelines

## 项目结构与模块组织
- `libs/deepagents/` 为核心库，源码在 `libs/deepagents/deepagents/`，测试在 `libs/deepagents/tests/`
- `libs/deepagents-cli/` 为 CLI，源码在 `libs/deepagents-cli/deepagents_cli/`，示例技能在 `libs/deepagents-cli/examples/skills/`
- `libs/acp/` 为 ACP 服务，源码在 `libs/acp/deepagents_acp/`，测试在 `libs/acp/tests/`
- `libs/harbor/` 为 Harbor 集成，源码在 `libs/harbor/deepagents_harbor/`，测试在 `libs/harbor/tests/`
- 每个子库都自带 `pyproject.toml`、`Makefile` 与 `uv.lock`，按子库独立开发与发布
- 根目录 `README.md` 提供整体背景与用法，子库 README 用于各组件的专项说明

## 构建、测试与开发命令
- 在各子库目录运行 `make` 目标，依赖使用 `uv` 管理
- `cd libs/deepagents && make test` 运行单元测试并输出覆盖率
- `cd libs/deepagents && make integration_test` 运行集成测试
- `cd libs/deepagents-cli && make run` 以 `uvx` 启动本地 CLI
- `cd libs/* && make lint` 或 `make format` 运行 ruff 格式化与检查
- 需要精确控制时可直接执行 `uv run pytest ...` 或 `uv run ruff check ...`

## 编码风格与命名约定
- Python 版本要求见各子库 `pyproject.toml`（核心库为 3.11+）
- 缩进 4 空格；类型标注优先；docstring 使用 Google 风格
- 格式化与静态检查使用 ruff，核心库启用 mypy 严格模式
- 模块与函数用 `snake_case`，类用 `PascalCase`
- 测试文件命名为 `test_*.py`，按功能拆分到 `unit_tests/` 或 `integration_tests/`

## 测试指南
- 测试框架为 pytest，按 `tests/unit_tests/` 与 `tests/integration_tests/` 划分
- 单文件测试示例：`cd libs/deepagents-cli && make test TEST_FILE=tests/unit_tests/test_config.py`
- 覆盖率仅在 `libs/deepagents` 的 `make test` 中默认开启
- 新增功能应同时补齐对应层级的测试，避免跨子库耦合用例

## 提交与 PR 指南
- 提交信息遵循 Conventional Commits：`feat(cli): ...`、`docs(harbor): ...`、`release(deepagents): ...`
- PR 目前无强制模板；建议包含：变更摘要、测试命令与结果、相关 Issue 链接
- 如修改 CLI 交互或输出格式，附示例日志或截图
- 若涉及多个子库，PR 描述中注明每个子库的变更点与影响范围

## 配置与安全提示
- 示例代码依赖 `TAVILY_API_KEY` 等环境变量时，避免提交真实密钥
- 涉及外部服务或沙箱执行的改动，请在 PR 描述中注明影响面
