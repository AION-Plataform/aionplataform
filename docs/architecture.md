# AION Platform Architecture

## System Overview
AION (AI-Oriented Organization Network) is a platform for orchestrating enterprise AI ecosystems. It follows a modular architecture separating design (Studio), validation (Compiler), and execution (Runtime), while adding integration, observability, governance, and a Copilot for guided creation.

## Architectural Principles
1. **Separation of Responsibilities**
   - Studio does not execute heavy logic.
   - Compiler does not render interfaces.
   - Runtime does not manipulate the UI graph.
2. **Industrialization (Fordist Model)**
   - Standardized nodes and versioned DSL.
   - Interchangeable components with clear contracts.
   - Repeatable templates per business domain.
3. **Controlled Experience**
   - Minimal UI with smart defaults.
   - Advanced configuration is optional.
   - Secure-by-default policies are enforced automatically.

```mermaid
graph TD
    User[User] -->|Interacts| Studio[AION Studio (Frontend)]
    
    subgraph "AION Core"
        Studio -->|JSON DSL| API[Runtime API (FastAPI)]
        API -->|Validates| Compiler[AION Compiler]
        Compiler -->|Generates| Plan[Execution Plan (DAG)]
        API -->|Triggers| Engine[Execution Engine]
        API -->|Persists| DB[(Execution Store)]
    end

    subgraph "Integration Layer"
        Engine -->|Invokes| LLM[LLM Gateways]
        Engine -->|Invokes| VectorDB[Vector DBs]
        Engine -->|Invokes| APIs[Enterprise APIs]
    end

    subgraph "Governance & Observability"
        Policy[Governance Engine] -->|Enforces| Engine
        Telemetry[Observability Layer] <-->|Traces/Logs| Engine
    end

    Copilot[AION Copilot] -->|Guided Ops| API
    Copilot -->|Suggests| Studio
```

## Data Flow
1.  **Design**: User constructs a flow in the Studio (React Flow).
    -   Output: `Flow Definition JSON` (versioned DSL).
2.  **Submission**: Studio sends DSL to `POST /flows` (Authenticated).
3.  **Compilation**:
    -   Compiler validates schemas, type compatibility, and cycles.
    -   Compiler applies defaults and generates a deterministic execution plan (DAG).
4.  **Execution Request**: User triggers `POST /flows/{id}/execute`.
5.  **Run**:
    -   Runtime executes the DAG in order with retries, timeouts, and caching.
    -   Context is passed between nodes with a typed contract.
    -   Observability emits traces/logs/metrics with a `trace_id`.
6.  **Governance**:
    -   Policy engine enforces cost limits, permissions, and auditability.

## Component Roles

### 1. Studio (`/studio`)
-   **Tech**: React, TypeScript, React Flow, Zustand.
-   **Role**: Visual builder (drag-and-drop), node configuration, DSL import/export.
-   **Constraints**: Does not execute heavy logic; only calls APIs.

### 2. Runtime (`/runtime`)
-   **Tech**: Python, FastAPI, AsyncIO, Redis, Docker.
-   **Role**: API gateway, execution orchestrator, context/state handling.
-   **Execution Metadata**: `execution_id`, `flow_id`, `start_time`, `latency`, `token_usage`, `cost_estimate`, `errors`, `trace_id`.

### 3. Compiler (`/compiler`)
-   **Tech**: Python, Pydantic, NetworkX.
-   **Role**: Graph traversal, validation, defaults, dependency resolution, plan generation.
-   **Output**: Deterministic `ExecutionPlan` with ordered steps, retries, timeouts, caching, and policy constraints.

### 4. Nodes (`/nodes`)
-   **Tech**: Python classes adhering to `Node` interface.
-   **Role**: Atomic units of work (e.g., `PDFLoader`, `OpenAIGenerator`).

### 5. Integration Layer
-   **Tech**: Connectors to OpenAI, open-source model APIs, LangChain, LlamaIndex, Qdrant, Pinecone.
-   **Role**: Standardized adapters for external AI infrastructure.

### 6. Observability Layer
-   **Tech**: OpenTelemetry, Prometheus.
-   **Role**: Traces, metrics, structured logs for runtime execution.

### 7. Governance Engine
-   **Role**: Policy enforcement, cost limits, permission controls, auditability.

### 8. AION Copilot
-   **Role**: Suggests flows, validates graphs, simulates execution, estimates cost.
-   **Rule**: Only acts via controlled APIs (never direct system mutation).
-   **Allowed Actions**: `create_node`, `update_node`, `connect_nodes`, `validate_graph`, `simulate_execution`, `suggest_optimization`, `estimate_cost`.

## Positioning
**AION is a Visual Platform for Industrializing Enterprise AI Ecosystems.** It orchestrates, standardizes, and governs AI flows without replacing the existing stack.
