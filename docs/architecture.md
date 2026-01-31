# AION Platform Architecture

## System Overview
AION (AI-Oriented Organization Network) is a platform for orchestrating AI agents and data flows. It follows a modular architecture separating design (Studio), validation (Compiler), and execution (Runtime).

```mermaid
graph TD
    User[User] -->|Interacts| Studio[AION Studio (Frontend)]
    
    subgraph "AION Core"
        Studio -->|JSON DSL| API[Runtime API (FastAPI)]
        API -->|Validates| Compiler[AION Compiler]
        Compiler -->|Generates| Plan[Execution Plan (DAG)]
        API -->|Persists| DB[(SQLite Database)]
        
        API -->|Triggers| Engine[Execution Engine]
        Engine -->|Reads| Plan
    end
    
    subgraph "Execution Layer"
        Engine -->|Invokes| Node1[Data Loader]
        Engine -->|Invokes| Node2[RAG Processor]
        Engine -->|Invokes| Node3[LLM Gateway]
    end
    
    Copilot[AION Copilot] -->|Generates/Validates| DSL[Flow DSL]
    API <--> Copilot
```

## Data Flow
1.  **Design**: User constructs a flow in the Studio (React Flow).
    -   Output: `Flow Definition JSON` (DSL).
2.  **Submission**: Studio sends DSL to `POST /flows` (Authenticated).
3.  **Persistence**: Runtime saves the DSL and metadata to `users` and `flows` tables in SQLite.
4.  **Execution Request**: User triggers `POST /flows/{id}/execute`.
5.  **Compilation**:
    -   Compiler validates the graph structure (cycles, missing inputs).
    -   Compiler generates a topological execution plan.
6.  **Run**:
    -   Background Task iterates through the plan.
    -   State is passed between nodes via a shared `Context`.
    -   Results are stored in `executions` table.

## Component Roles

### 1. Studio (`/studio`)
-   **Tech**: React, Vite, Tailwind, React Flow.
-   **Role**: Visual builder, Authentication UI, status monitoring.

### 2. Runtime (`/runtime`)
-   **Tech**: Python, FastAPI, SQLite, Pydantic.
-   **Role**: API Gateway, Auth provider, Execution Orchestrator.

### 3. Compiler (`/compiler`)
-   **Tech**: Python (NetworkX compatible logic).
-   **Role**: Graph traversal, validation, optimization.

### 4. Nodes (`/nodes`)
-   **Tech**: Python classes adhering to `Node` interface.
-   **Role**: Atomic units of work (e.g., `PDFLoader`, `OpenAIGenerator`).
