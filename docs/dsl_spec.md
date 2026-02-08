# AION Flow DSL Specification

The AION Domain Specific Language (DSL) is a JSON-based format for defining AI workflows. It is versioned, validated against a schema, and never stores secrets directly.

## Rules
- **Versioning is mandatory** for the DSL and each node type.
- **Secrets are never embedded**; they must be referenced via `secrets_reference`.
- **Schema validation is required** before compilation.
- **Backward compatibility is controlled**; breaking changes require a new major version.

## Schema Structure

```json
{
  "metadata": {
    "name": "string",
    "description": "string",
    "version": "1.0.0",
    "author": "string",
    "created_at": "ISO-8601"
  },
  "nodes": [
    {
      "id": "string (unique)",
      "type": "string (namespace.name)",
      "version": "string",
      "inputs": {
        "input_name": "source_node_id.output_name"
      },
      "outputs": {
        "output_name": "schema_ref"
      },
      "config": {
        "key": "value"
      },
      "policies": {
        "key": "value"
      }
    }
  ],
  "edges": [
    {
      "source": "node_id",
      "source_output": "output_name",
      "target": "node_id",
      "target_input": "input_name"
    }
  ],
  "secrets_reference": {
    "provider": "vault|env|kms",
    "refs": {
      "key": "external_secret_id"
    }
  },
  "policies": {
    "cost_limit_daily": "number",
    "allowed_models": ["string"]
  }
}
```

## Node Contract

```json
{
  "id": "string",
  "type": "string",
  "version": "string",
  "inputs": "schema",
  "outputs": "schema",
  "config": "object",
  "policies": "object"
}
```

## Node Types (Initial Set)

### Data (`loader.*`)
| Type | Config | Outputs | Description |
|------|--------|---------|-------------|
| `loader.pdf` | `path`: string | `content` | Extracts text from PDF. |
| `loader.sql` | `query`: string | `rows` | Loads data from SQL. |
| `loader.api` | `url`: string | `response` | Fetches data from an HTTP API. |
| `loader.web` | `url`: string | `content` | Scrapes content from a URL. |

### Transform (`transform.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `transform.clean` | `rules`: object | `content` | `cleaned` | Cleans text or records. |
| `transform.normalize` | `schema`: object | `records` | `normalized` | Normalizes records to schema. |

### RAG (`rag.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `rag.chunk` | `size`: int | `content` | `chunks` | Splits text into chunks. |
| `rag.embed` | `model`: string | `chunks` | `embeddings` | Vectorizes text chunks. |
| `rag.vector_store` | `index`: string | `embeddings` | `store_id` | Stores vectors in a vector DB. |
| `rag.retrieve` | `k`: int | `query`, `store_id` | `documents` | Retrieves relevant chunks. |

### LLM (`llm.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `llm.generate` | `model`: string, `prompt`: string | `context` | `output` | Generates text using LLM. |

### Agent & Tools (`agent.*`, `tool.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `agent.router` | `routes`: object | `input` | `route` | Routes to subflows/tools. |
| `tool.http` | `method`: string, `url`: string | `payload` | `response` | Calls an HTTP endpoint. |

### Output (`output.*`)
| Type | Config | Inputs | Outputs | Description |
|------|--------|--------|---------|-------------|
| `api.endpoint` | `path`: string | `result` | `response` | Exposes output via API. |

## Example: Simple RAG Flow

```json
{
  "metadata": { "name": "Simple RAG", "version": "1.0.0" },
  "nodes": [
    {
      "id": "src", 
      "type": "loader.pdf",
      "version": "1.0.0",
      "config": { "path": "/data/handbook.pdf" }
    },
    {
      "id": "chunky",
      "type": "rag.chunk",
      "version": "1.0.0",
      "inputs": { "content": "src.content" }
    },
    {
      "id": "gen",
      "type": "llm.generate",
      "version": "1.0.0",
      "config": { "prompt": "Summarize: {context}" },
      "inputs": { "context": "chunky.chunks" }
    }
  ],
  "edges": [
    { "source": "src", "source_output": "content", "target": "chunky", "target_input": "content" },
    { "source": "chunky", "source_output": "chunks", "target": "gen", "target_input": "context" }
  ],
  "secrets_reference": {
    "provider": "env",
    "refs": { "OPENAI_API_KEY": "OPENAI_API_KEY" }
  }
}
```
