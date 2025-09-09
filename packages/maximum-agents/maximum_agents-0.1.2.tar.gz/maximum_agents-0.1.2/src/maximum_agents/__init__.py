"""Maximum Agents Framework"""

from .document_types import DocumentT, DocumentsT
from smolagents import WebSearchTool, Tool
from .base import RetryingModel, BaseAgent
__all__ = ["DocumentT", "DocumentsT", "WebSearchTool", "Tool", "RetryingModel", "BaseAgent"]