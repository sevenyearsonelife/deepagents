# 🧠🤖 Deep Agents

使用 LLM 在循环中调用工具是智能体的最简单形式。然而，这种架构产生的智能体往往是"浅层"的，无法在更长、更复杂的任务中进行规划和行动。

诸如"Deep Research"、"Manus"和"Claude Code"等应用程序通过实现四个功能的组合来克服这一限制：**规划工具**、**子智能体**、访问**文件系统**和**详细的提示词**。

<img src="../../deep_agents.png" alt="deep agent" width="600"/>

`deepagents` 是一个以通用方式实现这些功能的 Python 包，以便您可以为应用程序轻松创建深度智能体。有关 `deepagents` 的完整概述和快速入门，最好的资源是我们的[文档](https://docs.langchain.com/oss/python/deepagents/overview)。

**致谢：该项目主要受 Claude Code 启发，最初很大程度上是为了解构 Claude Code 的核心原理并将其更加通用化。**

## 安装

```bash
# pip
pip install deepagents

# uv
uv add deepagents

# poetry
poetry add deepagents
```

## 使用方法

（要运行下面的示例，您需要先执行 `pip install tavily-python`）。

请确保在环境中设置了 `TAVILY_API_KEY`。您可以[在这里](https://www.tavily.com/)生成一个。

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# 网络搜索工具
def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """运行网络搜索"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )


# 用于引导智能体成为专家研究人员的系统提示词
research_instructions = """你是一位专家级研究员。你的工作是进行全面的研究，然后撰写一份精美的报告。

你可以使用网络搜索工具作为收集信息的主要手段。

## `internet_search`

使用此工具对给定查询运行网络搜索。您可以指定返回的最大结果数、主题以及是否包含原始内容。
"""

# 创建深度智能体
agent = create_deep_agent(
    tools=[internet_search],
    system_prompt=research_instructions,
)

# 调用智能体
result = agent.invoke({"messages": [{"role": "user", "content": "什么是 langgraph?"}]})
```

更复杂的示例请参见 [examples/research/research_agent.py](examples/research/research_agent.py)。

使用 `create_deep_agent` 创建的智能体就是一个 LangGraph 图——因此您可以像与任何 LangGraph 智能体交互一样与它交互（流式传输、人在回路、记忆、studio）。

## 核心能力

**规划与任务分解**

深度智能体包含内置的 `write_todos` 工具，使智能体能够将复杂任务分解为离散的步骤，跟踪进度，并在新信息出现时调整计划。

**上下文管理**

文件系统工具（`ls`、`read_file`、`write_file`、`edit_file`、`glob`、`grep`）允许智能体将大型上下文卸载到内存中，防止上下文窗口溢出，并能够处理可变长度的工具结果。

**子智能体派生**

内置的 `task` 工具使智能体能够派生专门的子智能体进行上下文隔离。这使主智能体的上下文保持清洁，同时仍能深入研究特定的子任务。

**长期记忆**

使用 LangGraph 的 Store 跨线程扩展智能体的持久记忆。智能体可以保存和检索以前对话中的信息。

## 自定义深度智能体

您可以通过向 `create_deep_agent` 传递多个参数来创建自己的自定义深度智能体。

### `model`

默认情况下，`deepagents` 使用 `"claude-sonnet-4-5-20250929"`。您可以通过传递任何 [LangChain 模型对象](https://python.langchain.com/docs/integrations/chat/)来自定义它。

```python
from langchain.chat_models import init_chat_model
from deepagents import create_deep_agent

model = init_chat_model("openai:gpt-4o")
agent = create_deep_agent(
    model=model,
)
```

### `system_prompt`

深度智能体带有内置的系统提示词。这是一个相对详细的提示词，很大程度上基于并受到[尝试](https://github.com/kn1026/cc/blob/main/claudecode.md)[复制](https://github.com/asgeirtj/system_prompts_leaks/blob/main/Anthropic/claude-code.md) Claude Code 系统提示词的启发。它比 Claude Code 的系统提示词更加通用。默认提示词包含有关如何使用内置规划工具、文件系统工具和子智能体的详细说明。

每个针对特定用例量身定制的深度智能体还应包含针对该用例的自定义系统提示词。提示词对于创建成功的深度智能体的重要性怎么强调都不为过。

```python
from deepagents import create_deep_agent

research_instructions = """你是一位专家级研究员。你的工作是进行全面的研究，然后撰写一份精美的报告。
"""

agent = create_deep_agent(
    system_prompt=research_instructions,
)
```

### `tools`

就像使用工具调用智能体一样，您可以为深度智能体提供一组它可以访问的工具。

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """运行网络搜索"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

agent = create_deep_agent(
    tools=[internet_search]
)
```

### `middleware`

`create_deep_agent` 使用可以自定义的中间件实现。您可以提供额外的中间件来扩展功能、添加工具或实现自定义钩子。

```python
from langchain_core.tools import tool
from deepagents import create_deep_agent
from langchain.agents.middleware import AgentMiddleware

@tool
def get_weather(city: str) -> str:
    """获取城市的天气。"""
    return f"{city} 的天气是晴天。"

@tool
def get_temperature(city: str) -> str:
    """获取城市的温度。"""
    return f"{city} 的温度是 70 华氏度。"

class WeatherMiddleware(AgentMiddleware):
  tools = [get_weather, get_temperature]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[WeatherMiddleware()]
)
```

### `subagents`

深度智能体的主要功能之一是能够派生子智能体。您可以在 subagents 参数中指定自定义子智能体，让智能体可以将工作移交给它们。子智能体对于上下文隔离（有助于不污染主智能体的整体上下文）以及自定义指令非常有用。

`subagents` 应该是一个字典列表，每个字典遵循以下架构：

```python
class SubAgent(TypedDict):
    name: str
    description: str
    system_prompt: str
    tools: Sequence[BaseTool | Callable | dict[str, Any]]
    model: NotRequired[str | BaseChatModel]
    middleware: NotRequired[list[AgentMiddleware]]
    interrupt_on: NotRequired[dict[str, bool | InterruptOnConfig]]

class CompiledSubAgent(TypedDict):
    name: str
    description: str
    runnable: Runnable
```

**SubAgent 字段：**
- **name**：这是子智能体的名称，也是主智能体调用子智能体的方式
- **description**：这是向主智能体显示的子智能体描述
- **system_prompt**：这是用于子智能体的系统提示词
- **tools**：这是子智能体可以访问的工具列表
- **model**：可选的模型名称或模型实例
- **middleware**：要附加到子智能体的额外中间件。有关中间件的介绍以及它如何与 create_agent 配合使用，请参见[此处](https://docs.langchain.com/oss/python/langchain/middleware)
- **interrupt_on**：自定义中断配置，指定工具的人机交互

**CompiledSubAgent 字段：**
- **name**：这是子智能体的名称，也是主智能体调用子智能体的方式
- **description**：这是向主智能体显示的子智能体描述
- **runnable**：将用作子智能体的预构建 LangGraph 图/智能体

#### 使用 SubAgent

```python
import os
from typing import Literal
from tavily import TavilyClient
from deepagents import create_deep_agent

tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

def internet_search(
    query: str,
    max_results: int = 5,
    topic: Literal["general", "news", "finance"] = "general",
    include_raw_content: bool = False,
):
    """运行网络搜索"""
    return tavily_client.search(
        query,
        max_results=max_results,
        include_raw_content=include_raw_content,
        topic=topic,
    )

research_subagent = {
    "name": "research-agent",
    "description": "用于更深入地研究问题",
    "system_prompt": "你是一位优秀的研究员",
    "tools": [internet_search],
    "model": "openai:gpt-4o",  # 可选覆盖，默认为主智能体模型
}
subagents = [research_subagent]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    subagents=subagents
)
```

#### 使用 CustomSubAgent

对于更复杂的用例，您可以提供自己的预构建 LangGraph 图作为子智能体：

```python
# 创建自定义智能体图
custom_graph = create_agent(
    model=your_model,
    tools=specialized_tools,
    prompt="你是数据分析的专用智能体..."
)

# 将其用作自定义子智能体
custom_subagent = CompiledSubAgent(
    name="data-analyzer",
    description="用于复杂数据分析任务的专用智能体",
    runnable=custom_graph
)

subagents = [custom_subagent]

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[internet_search],
    system_prompt=research_instructions,
    subagents=subagents
)
```

### `interrupt_on`

智能体的一个常见现实情况是，某些工具操作可能是敏感的，需要在执行前获得人工批准。深度智能体通过 LangGraph 的中断能力支持人在回路工作流。您可以使用检查点配置器配置哪些工具需要批准。

这些工具配置被传递到我们预构建的 [HITL 中间件](https://docs.langchain.com/oss/python/langchain/middleware#human-in-the-loop)，以便智能体暂停执行并等待用户在执行配置的工具之前提供反馈。

```python
from langchain_core.tools import tool
from deepagents import create_deep_agent

@tool
def get_weather(city: str) -> str:
    """获取城市的天气。"""
    return f"{city} 的天气是晴天。"

agent = create_deep_agent(
    model="anthropic:claude-sonnet-4-20250514",
    tools=[get_weather],
    interrupt_on={
        "get_weather": {
            "allowed_decisions": ["approve", "edit", "reject"]
        },
    }
)

```

## 深度智能体中间件

深度智能体采用模块化的中间件架构构建。提醒一下，深度智能体可以访问：
- 规划工具
- 用于存储上下文和长期记忆的文件系统
- 派生子智能体的能力

这些功能中的每一个都作为单独的中间件实现。当您使用 `create_deep_agent` 创建深度智能体时，我们会自动将 **TodoListMiddleware**、**FilesystemMiddleware** 和 **SubAgentMiddleware** 附加到您的智能体。

中间件是一个可组合的概念，您可以根据用例选择向智能体添加任意数量的中间件。这意味着您也可以独立使用上述任何中间件！

### TodoListMiddleware

规划是解决复杂问题的核心。如果您最近使用过 claude code，您会注意到它在处理复杂的多部分任务之前会写出待办事项列表。您还会注意到，随着更多信息的到来，它可以即时调整和更新此待办事项列表。

**TodoListMiddleware** 为您的智能体提供了一个专门用于更新此待办事项列表的工具。在执行多部分任务之前和期间，智能体会被提示使用 write_todos 工具来跟踪它正在做的事情以及仍需要做的事情。

```python
from langchain.agents import create_agent
from langchain.agents.middleware import TodoListMiddleware

# TodoListMiddleware 默认包含在 create_deep_agent 中
# 如果构建自定义智能体，您可以自定义它
agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    # 可以通过中间件添加自定义规划指令
    middleware=[
        TodoListMiddleware(
            system_prompt="使用 write_todos 工具来..."  # 可选：系统提示词的自定义添加
        ),
    ],
)
```

### FilesystemMiddleware

上下文工程是构建有效智能体的主要挑战之一。当使用可以返回可变长度结果（例如 web_search、rag）的工具时，这可能尤其困难，因为长的 ToolResults 会很快填满您的上下文窗口。
**FilesystemMiddleware** 为您的智能体提供了四种工具来与短期和长期记忆交互。
- **ls**：列出文件系统中的文件
- **read_file**：读取整个文件或文件中的特定行数
- **write_file**：向文件系统写入新文件
- **edit_file**：编辑文件系统中的现有文件

```python
from langchain.agents import create_agent
from deepagents.middleware.filesystem import FilesystemMiddleware


# FilesystemMiddleware 默认包含在 create_deep_agent 中
# 如果构建自定义智能体，您可以自定义它
agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        FilesystemMiddleware(
            backend=..., # 可选：自定义存储后端
            system_prompt="在...时写入文件系统",  # 可选的自定义系统提示词覆盖
            custom_tool_descriptions={
                "ls": "在...时使用 ls 工具",
                "read_file": "使用 read_file 工具来..."
            }  # 可选：文件系统工具的自定义描述
        ),
    ],
)
```

### SubAgentMiddleware

将任务移交给子智能体是隔离上下文的好方法，在保持主（主管）智能体上下文窗口清洁的同时仍能深入研究任务。子智能体中间件允许您通过任务工具提供子智能体。

子智能体通过名称、描述、系统提示词和工具来定义。您还可以为子智能体提供自定义模型或额外的中间件。当您想给子智能体一个额外的状态键以与主智能体共享时，这特别有用。

```python
from langchain_core.tools import tool
from langchain.agents import create_agent
from deepagents.middleware.subagents import SubAgentMiddleware


@tool
def get_weather(city: str) -> str:
    """获取城市的天气。"""
    return f"{city} 的天气是晴天。"

agent = create_agent(
    model="claude-sonnet-4-20250514",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-20250514",
            default_tools=[],
            subagents=[
                {
                    "name": "weather",
                    "description": "此子智能体可以获取城市的天气。",
                    "system_prompt": "使用 get_weather 工具获取城市的天气。",
                    "tools": [get_weather],
                    "model": "gpt-4.1",
                    "middleware": [],
                }
            ],
        )
    ],
)
```

对于更复杂的用例，您还可以提供自己的预构建 LangGraph 图作为子智能体。

```python
# 创建自定义 LangGraph 图
def create_weather_graph():
    workflow = StateGraph(...)
    # 构建自定义图
    return workflow.compile()

weather_graph = create_weather_graph()

# 将其包装在 CompiledSubAgent 中
weather_subagent = CompiledSubAgent(
    name="weather",
    description="此子智能体可以获取城市的天气。",
    runnable=weather_graph
)

agent = create_agent(
    model="anthropic:claude-sonnet-4-20250514",
    middleware=[
        SubAgentMiddleware(
            default_model="claude-sonnet-4-20250514",
            default_tools=[],
            subagents=[weather_subagent],
        )
    ],
)
```

## 同步与异步

deepagents 的早期版本分离了同步和异步智能体工厂。

`async_create_deep_agent` 已被合并到 `create_deep_agent` 中。

**您应该使用 `create_deep_agent` 作为同步和异步智能体的工厂**


## MCP

`deepagents` 库可以与 MCP 工具一起运行。这可以通过使用 [Langchain MCP 适配器库](https://github.com/langchain-ai/langchain-mcp-adapters)来实现。

**注意：** MCP 工具是异步的，因此您需要使用 `agent.ainvoke()` 或 `agent.astream()` 进行调用。

（要运行下面的示例，需要执行 `pip install langchain-mcp-adapters`）

```python
import asyncio
from langchain_mcp_adapters.client import MultiServerMCPClient
from deepagents import create_deep_agent

async def main():
    # 收集 MCP 工具
    mcp_client = MultiServerMCPClient(...)
    mcp_tools = await mcp_client.get_tools()

    # 创建智能体
    agent = create_deep_agent(tools=mcp_tools, ....)

    # 流式传输智能体
    async for chunk in agent.astream(
        {"messages": [{"role": "user", "content": "什么是 langgraph?"}]},
        stream_mode="values"
    ):
        if "messages" in chunk:
            chunk["messages"][-1].pretty_print()

asyncio.run(main())
```
