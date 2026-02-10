# Novo Projeto (clean restart)

Projeto novo e mínimo com login/registro funcional.

## Subir localmente

```bash
cd novo_projeto
docker compose up --build
```

- Web: http://localhost:8080
- API: http://localhost:8000/health

## Fluxo
1. Registrar usuário
2. Entrar
3. Clicar em `Ver /me`

## Observação importante
A página valida `content-type` JSON para evitar erro do tipo `Unexpected token '<'` quando houver proxy/API mal configurado.
