# AION Flow DSL Specification

The AION Domain Specific Language (DSL) is a JSON-based format for defining AI workflows.

## Schema Structure

```json
{
  "metadata": {
    "name": "string",
    "description": "string",
    "version": "1.0",
    "author": "string"
  },
  "nodes": [
    {
      "id": "string (unique)",
      "type": "string (namespace.name)",
      "config": {
        "key": "value"
      },
      "inputs": {
        "input_name": "source_node_id.output_name"
      }
    }
  ]
}
```

## Node Types

### Data Loaders (`loader.*`)
| Type | Config | Outputs | Description |
|------|--------|---------|-------------|
| `loader.static` | `text`: string | `content` | Emits static text. |
| `loader.pdf` | `path`: string | `content` | Extracts text from PDF. |
| `loader.web` | `url`: string | `content` | Scrapes text from URL. |

### RAG Operations (`rag.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `rag.chunk` | `size`: int | `text` | `chunks` | Splits text into chunks. |
| `rag.embed` | `model`: string | `chunks` | `embeddings` | Vectorizes text chunks. |
| `rag.vector_store` | - | `embeddings` | `store_id` | Stores vectors in memory. |
| `rag.retrieve` | `k`: int | `query`, `store` | `documents` | Retrieves relevant chunks. |

### Intelligence (`llm.*`, `agent.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `llm.generate` | `model`: string, `prompt`: string | `context` | `output` | Generates text using LLM. |

## Example: Simple RAG Flow

```json
{
  "metadata": { "name": "Simple RAG" },
  "nodes": [
    {
      "id": "src", 
      "type": "loader.static", 
      "config": { "text": "AION is a platform..." }
    },
    {
      "id": "chunky",
      "type": "rag.chunk",
      "inputs": { "text": "src.content" }
    },
    {
      "id": "gen",
      "type": "llm.generate",
      "config": { "prompt": "Summarize: {context}" },
      "inputs": { "context": "chunky.chunks" }
    }
  ]
}
```
