# 1. 直接导入！不需要任何 sys.path.append() 黑魔法
# 因为 .venv 里的快捷方式已经告诉 Python 去哪里找源码了
import deepagents

print(f"DeepAgents 包位置: {deepagents.__file__}")
