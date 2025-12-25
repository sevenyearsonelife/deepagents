# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

**DeepAgents** 是一个开源的 "深度智能体" (Deep Agent) 框架，用于构建能够处理长时程复杂任务的 AI 智能体。项目采用 monorepo 结构，包含多个 Python 包：

- `libs/deepagents/` - 核心库，提供 `create_deep_agent()` 工厂函数
- `libs/deepagents-cli/` - CLI 工具，类似 Claude Code 的交互式终端助手
- `libs/harbor/` - Terminal Bench 2.0 评估集成
- `libs/acp/` - Agent Client Protocol 支持

## 常用命令

### 依赖安装

项目使用 **uv** 作为包管理器：

```bash
# 安装所有依赖（包括开发依赖）
cd libs/deepagents && uv sync --all-groups
cd libs/deepagents-cli && uv sync --all-groups
cd libs/harbor && uv sync --all-groups
```

### 测试

```bash
# 核心库 - 单元测试
cd libs/deepagents && make test
# 或运行特定测试文件
make test TEST_FILE=tests/unit_tests/test_middleware.py

# 核心库 - 集成测试
cd libs/deepagents && make integration_test

# CLI - 单元测试
cd libs/deepagents-cli && make test
# 或运行特定测试文件
make test TEST_FILE=tests/unit_tests/test_file_ops.py

# CLI - 集成测试
cd libs/deepagents-cli && make test_integration

# Harbor
cd libs/harbor && make test
```

### Lint 和 Format

```bash
# 核心库
cd libs/deepagents && make lint      # 检查（ruff + mypy）
cd libs/deepagents && make format    # 格式化代码

# CLI
cd libs/deepagents-cli && make lint
cd libs/deepagents-cli && make format

# Harbor
cd libs/harbor && make lint
cd libs/harbor && make format
```

### 运行 CLI

```bash
# 从源码运行
cd libs/deepagents-cli && make run
# 或
uv run deepagents

# 安装后运行
deepagents
deepagents --agent mybot
deepagents --model claude-sonnet-4-5-20250929
deepagents --auto-approve
deepagents --sandbox modal
```

### Harbor 评估

```bash
cd libs/harbor

# 在 Docker 上运行 1 个 Terminal Bench 任务（快速测试）
make run-terminal-bench-docker

# 在 Modal 上运行 4 个任务
make run-terminal-bench-modal

# 在 Daytona 上运行 40 个任务
make run-terminal-bench-daytona

# 在 Runloop 上运行 10 个任务
make run-terminal-bench-runloop

# 运行 hello-world 测试
make run-hello-world
```

## 架构概览

### 核心设计模式：中间件架构

`create_deep_agent()` 通过组合多个中间件来构建智能体：

```
create_deep_agent()
    ↓
添加默认中间件:
    ├── TodoListMiddleware        # 任务规划工具 (write_todos)
    ├── FilesystemMiddleware      # 文件系统工具
    ├── SubAgentMiddleware        # 子智能体工具
    ├── SummarizationMiddleware   # 上下文摘要（超过 170k tokens）
    ├── AnthropicPromptCachingMiddleware  # 提示词缓存（Anthropic）
    └── PatchToolCallsMiddleware  # 修复中断的工具调用
    ↓
返回 CompiledStateGraph (LangGraph)
```

### 内置工具

| 工具名称 | 描述 | 提供者 |
|---------|------|--------|
| `write_todos`, `read_todos` | 任务规划和进度跟踪 | TodoListMiddleware |
| `ls`, `read_file`, `write_file`, `edit_file`, `glob`, `grep` | 文件系统操作 | FilesystemMiddleware |
| `execute` | Shell 命令执行（仅沙箱模式） | FilesystemMiddleware |
| `task` | 委托子智能体 | SubAgentMiddleware |

### 存储后端架构

```
BackendProtocol (接口)
    ├── StateBackend             # 内存中，默认
    ├── FilesystemBackend        # 真实磁盘访问
    ├── StoreBackend             # LangGraph Store 持久化
    ├── CompositeBackend         # 路由到多个后端
    └── SandboxBackendProtocol   # 沙箱执行
```

### CLI 架构

```
cli_main() → main() → _run_agent_session() → simple_cli()
    ↓
create_cli_agent()
    ├── 加载 agent.md（全局 + 项目）
    ├── 设置 CompositeBackend
    ├── 添加 SkillsMiddleware
    └── 配置沙箱 (modal/daytona/runloop)
    ↓
simple_cli() - 主 REPL 循环
```

### 技能系统

```
~/.deepagents/<agent>/skills/     # 全局技能
.deepagents/skills/               # 项目技能

SkillsMiddleware → 渐进式披露模式:
    ├── 启动时扫描技能目录
    ├── 解析 YAML frontmatter（名称 + 描述）
    ├── 将技能列表注入提示词
    └── 按需读取完整 SKILL.md
```

## 项目结构

```
deepagents/
├── libs/
│   ├── deepagents/               # 核心库
│   │   ├── deepagents/
│   │   │   ├── __init__.py       # 导出 create_deep_agent
│   │   │   ├── graph.py          # 主工厂函数
│   │   │   ├── middleware/       # 中间件实现
│   │   │   └── backends/         # 存储后端
│   │   ├── tests/
│   │   │   ├── unit_tests/
│   │   │   └── integration_tests/
│   │   └── Makefile
│   │
│   ├── deepagents-cli/           # CLI 工具
│   │   ├── deepagents_cli/
│   │   │   ├── main.py           # CLI 主入口
│   │   │   ├── agent.py          # 智能体创建
│   │   │   ├── execution.py      # 任务执行逻辑
│   │   │   ├── tools.py          # CLI 特定工具
│   │   │   ├── skills/           # 技能系统
│   │   │   └── integrations/     # 沙箱集成
│   │   ├── examples/skills/      # 示例技能
│   │   └── Makefile
│   │
│   ├── harbor/                   # Terminal Bench 评估
│   │   ├── deepagents_harbor/
│   │   │   ├── deepagents_wrapper.py
│   │   │   └── backend.py
│   │   └── Makefile
│   │
│   └── acp/                      # Agent Client Protocol
│
├── .github/workflows/             # CI/CD
└── README.md
```

## 重要约定

### 中间件开发

- 所有中间件继承 `langchain.agents.middleware.AgentMiddleware`
- 中间件通过 `tools` 属性注入工具
- 通过 `system_prompt` 属性添加提示词指令
- 参考 `deepagents/middleware/` 下的现有实现

### 后端开发

- 所有后端实现 `deepagents.backends.protocol.BackendProtocol`
- `SandboxBackendProtocol` 扩展了基本的 shell 执行能力
- `CompositeBackend` 支持按路径路由到不同后端

### CLI 技能开发

- 技能文件包含 YAML frontmatter（name + description）
- 使用渐进式披露：智能体知道技能存在，但只在需要时读取完整指令
- 技能可以放在全局（`~/.deepagents/<agent>/skills/`）或项目（`.deepagents/skills/`）

### 配置文件位置

| 配置类型 | 全局位置 | 项目位置 |
|---------|---------|---------|
| agent.md | `~/.deepagents/<agent>/agent.md` | `.deepagents/agent.md` |
| 技能 | `~/.deepagents/<agent>/skills/` | `.deepagents/skills/` |
| 记忆文件 | `~/.deepagents/<agent>/memories/` | `.deepagents/memories/` |

## 环境变量

| 变量 | 用途 |
|------|------|
| `ANTHROPIC_API_KEY` | Anthropic 模型访问 |
| `OPENAI_API_KEY` | OpenAI 模型访问 |
| `GOOGLE_API_KEY` | Google 模型访问 |
| `TAVILY_API_KEY` | 网络搜索（CLI 默认工具） |
| `LANGCHAIN_TRACING_V2` | 启用 LangSmith |
| `LANGCHAIN_API_KEY` | LangSmith API 密钥 |
| `DEEPAGENTS_LANGSMITH_PROJECT` | 智能体追踪项目 |
| `LANGSMITH_PROJECT` | 用户代码追踪项目 |

## 关键设计原则

1. **信任 LLM 模型** - 安全边界在工具/沙箱级别强制执行，不依赖 LLM 自我约束
2. **渐进式披露** - 智能体知道技能存在，但只在需要时读取完整指令
3. **上下文卸载** - 大型工具结果自动保存到文件系统
4. **复合记忆** - 工作文件保持临时，重要数据持久化
5. **沙箱执行** - 支持 Modal、Daytona、Runloop 进行远程代码执行
