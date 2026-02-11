# Studio ↔ Runtime API Connections

Este documento mapeia todas as conexões do frontend Studio para a API Runtime.

## Base URL resolution

Arquivo: `studio/src/lib/api.ts`

Ordem de resolução:
1. `window.__AION_CONFIG__.API_BASE_URL` (runtime-config)
2. `VITE_API_BASE_URL` (build-time)
3. fallback `/api`

Compatibilidade:
- Se existir mais de uma base candidata (`/api` e `''`), o client testa `GET /health` e prioriza automaticamente a base saudável.
- Se base preferida for `/api`, o client tenta fallback para raiz (`''`) quando recebe resposta típica de proxy quebrado:
  - `text/html`
  - respostas não-JSON
  - status `404`, `405`, `502`, `503`, `504`

## Conexões por componente

### Login (`studio/src/components/Login.tsx`)
- `POST /auth/register`
  - body JSON `{ username, password }`
- `POST /auth/token`
  - body `FormData` (`username`, `password`)
- O parse de resposta faz leitura segura (`res.text()` + `JSON.parse`) e mostra diagnóstico com URL final/status/content-type quando vier HTML em vez de JSON.

### Flow Library (`studio/src/components/FlowLibrary.tsx`)
- `GET /flows`
- `DELETE /flows/{id}`
- `POST /flows/{id}/execute`
- Todos com header `Authorization: Bearer <token>`.

### Flow Editor (`studio/src/components/FlowEditor.tsx`)
- `POST /flows`
- Header `Authorization: Bearer <token>`.

### Secrets Vault (`studio/src/components/SecretsVault.tsx`)
- `GET /secrets`
- `POST /secrets`
- `DELETE /secrets/{id}`
- Todos com header `Authorization: Bearer <token>`.

## Runtime endpoints esperados

Arquivo: `runtime/main.py`

- `POST /auth/register`
- `POST /auth/token`
- `GET /flows`
- `POST /flows`
- `DELETE /flows/{flow_id}`
- `POST /flows/{flow_id}/execute`
- `GET /secrets`
- `POST /secrets`
- `DELETE /secrets/{secret_id}`

## Checklist de deploy

1. Garantir API acessível por uma das rotas:
   - `/api/*` **ou**
   - `/*` (root)
2. Definir CORS corretamente no Runtime (`CORS_ORIGINS`).
3. Confirmar token no `localStorage` (`aion_token`) após login.
4. Verificar no browser devtools que `POST /auth/token` retorna JSON.

## Persistência de usuários

Arquivo: `runtime/database.py`

- Usuários são salvos no banco SQLite `aion.db`, tabela `users`.
- Campos: `id`, `username`, `hashed_password`.
- `username` é único e senha é armazenada com hash (`pbkdf2_sha256`, em `runtime/auth.py`).
