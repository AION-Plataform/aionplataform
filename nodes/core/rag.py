from typing import Dict, Any, List
from .base import BaseNode

class ChunkTextNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        content = inputs.get("content", "")
        # Handle cases where input is a dict from previous node
        if isinstance(inputs, dict):
             # Try to find 'content' from any input source
             for k, v in inputs.items():
                 if isinstance(v, dict) and "content" in v:
                     content = v["content"]
                     break
        
        chunk_size = self.config.get("size", 1000)
        overlap = self.config.get("overlap", 100)
        
        print(f"  [ChunkText] Chunking content (len={len(content)}) into chunks of {chunk_size}")
        
        # Mock chunking
        chunks = [content[i:i+chunk_size] for i in range(0, len(content), chunk_size - overlap)]
        return {"chunks": chunks}

class EmbedNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        chunks = []
        # Extract chunks from inputs
        for v in inputs.values():
            if isinstance(v, dict) and "chunks" in v:
                chunks = v["chunks"]
                break
        
        model = self.config.get("model", "openai/text-embedding-3-small")
        print(f"  [Embed] Embedding {len(chunks)} chunks using {model}")
        
        # Mock embeddings
        embeddings = [[0.1, 0.2, 0.3] for _ in chunks]
        return {"embeddings": embeddings, "chunks": chunks}

class VectorStoreNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        # Would normally connect to Qdrant/Pinecone
        print("  [VectorStore] Storing embeddings...")
        return {"status": "indexed", "count": 10}

class RetrieveNode(BaseNode):
    async def execute(self, inputs: Dict[str, Any]) -> Dict[str, Any]:
        query = inputs.get("query", "test query")
        print(f"  [Retrieve] Searching for: {query}")
        
        # Mock retrieval results
        return {
            "documents": [
                {"content": "Retrieved doc 1", "score": 0.9},
                {"content": "Retrieved doc 2", "score": 0.8}
            ]
        }
