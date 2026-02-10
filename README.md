# AION Platform
**AI-Oriented Organization Network**

AION is a comprehensive platform for designing, validating, and executing AI agent workflows. It enables "Fordist" assembly lines for AI, moving away from artisanal scripts to robust, observable pipelines.

## 🚀 Features

-   **AION Studio**: Visual Flow Builder (React + Vite + React Flow).
    -   *Premium UI*: Glassmorphism, Dark Mode, Animations.
    -   *Drag & Drop*: Intuitive canvas for constructing DAGs.
-   **AION Runtime**: High-performance Execution Engine (FastAPI + Python).
    -   *Persistence*: SQLite-based history of Flows and Executions.
    -   *Security*: JWT Authentication and User Ownership.
-   **AION Copilot**: AI Assistant.
    -   Generates flow structures from natural language.
    -   Validates pipelines and suggests improvements.
-   **Infrastructure**: Production-ready.
    -   Docker Compose for local dev.
    -   Kubernetes manifests for scaling.

## 📂 Project Structure

```
aion/
├── studio/         # Frontend (React + Vite)
├── runtime/        # Backend API & Executor (FastAPI)
├── compiler/       # Validation Logic & Planning
├── nodes/          # Atomic logic units (Loaders, RAG, LLM)
├── schemas/        # JSON DSL Specifications
├── docs/           # Architecture & Specs
└── infra/          # Docker & Kubernetes config
```

## 🛠️ Quick Start

### Prerequisites
-   Docker & Docker Compose
-   Node.js 18+ (for local Studio dev)
-   Python 3.11+ (for local Runtime dev)

### Environment Setup
> [!IMPORTANT]
> Before running, copy `.env.example` to `.env` and configure your environment variables.

```bash
cp .env.example .env
```

For production, **generate new secure keys**:
```bash
# Generate SECRET_KEY (at least 32 characters)
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Generate ENCRYPTION_KEY (Fernet key)
python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
```

Update `.env` with the generated keys.

### Run with Docker (Recommended)
```bash
docker-compose up --build
```
Access the **Studio** at `http://localhost:5173` and the **API** at `http://localhost:8000`.


### Dockerfile de instalação (API)
Se quiser construir apenas a imagem da API com instalação de dependências e validação de import:

```bash
docker build -f Dockerfile.install -t aion-install .
docker run --rm -p 8000:8000 aion-install
```

A API ficará disponível em `http://localhost:8000`.

### Run Manually

**1. Backend**
```bash
pip install -r requirements.txt
uvicorn runtime.main:app --reload
```

**2. Frontend**
```bash
cd studio
npm install
npm run dev
```
Access the Studio at `http://localhost:5173`.

## 📚 Documentation
-   [Architecture Overview](docs/architecture.md)
-   [DSL Specification](docs/dsl_spec.md)

## 🔐 Security
Default credentials for local dev (if using seeded DB):
-   **Register a new user** in the Studio login screen.
-   Flows are private to the user who created them.

## License
Proprietary / Internal Use Only.
