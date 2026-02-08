from typing import Type
from .core.base import BaseNode
from .core.loaders import PdfLoaderNode, StaticTextNode, SqlLoaderNode, ApiLoaderNode, WebLoaderNode
from .core.transforms import CleanTextNode, NormalizeNode
from .core.rag import ChunkTextNode, EmbedNode, VectorStoreNode, RetrieveNode
from .core.llm import LLMGenerateNode, AgentRouterNode
from .core.tools import HttpToolNode
from .core.outputs import ApiEndpointNode

class NodeRegistry:
    _registry = {
        "loader.pdf": PdfLoaderNode,
        "loader.static": StaticTextNode,
        "loader.sql": SqlLoaderNode,
        "loader.api": ApiLoaderNode,
        "loader.web": WebLoaderNode,
        "transform.clean": CleanTextNode,
        "transform.normalize": NormalizeNode,
        "rag.chunk": ChunkTextNode,
        "rag.embed": EmbedNode,
        "rag.vector_store": VectorStoreNode,
        "rag.retrieve": RetrieveNode,
        "llm.generate": LLMGenerateNode,
        "agent.router": AgentRouterNode,
        "agent.react": AgentRouterNode,
        "tool.http": HttpToolNode,
        "api.endpoint": ApiEndpointNode,
    }

    @classmethod
    def get_node_class(cls, node_type: str) -> Type[BaseNode]:
        node_class = cls._registry.get(node_type)
        if not node_class:
            raise ValueError(f"Unknown node type: {node_type}")
        return node_class

    @classmethod
    def register(cls, node_type: str, node_class: Type[BaseNode]):
        cls._registry[node_type] = node_class
