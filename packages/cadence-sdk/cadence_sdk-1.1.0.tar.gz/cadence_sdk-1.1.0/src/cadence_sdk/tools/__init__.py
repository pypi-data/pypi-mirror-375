"""Tool utilities for Cadence plugins.

Re-exports LangChain tool types and provides tool registration functionality.
"""

from langchain_core.tools import Tool

from .decorators import tool

type AgentTool = Tool

__all__ = ["Tool", "tool"]
