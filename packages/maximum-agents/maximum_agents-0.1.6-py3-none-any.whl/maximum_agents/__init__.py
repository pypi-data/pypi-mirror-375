"""Maximum Agents Framework"""

from .document_types import DocumentT, DocumentsT
from smolagents import WebSearchTool, Tool
from .base import RetryingModel, BaseAgent
from .builders.builder import AgentBuilder
from .tools import GetDocumentTool, GetPresentationTool, GetClientTool  
__all__ = ["DocumentT", "DocumentsT", "WebSearchTool", "Tool", "RetryingModel", "BaseAgent", "AgentBuilder", "GetDocumentTool", "GetPresentationTool", "GetClientTool"]