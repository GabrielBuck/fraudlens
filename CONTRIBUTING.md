# Contribuindo

## Setup

Use `scripts/setup.ps1` no Windows ou `scripts/setup.sh` no macOS/Linux. Inicialize o banco e rode `fraudlens pipeline run-all` antes de iniciar backend e frontend.

## Fluxo de trabalho

- Crie uma branch curta a partir da principal: `feat/nome`, `fix/nome` ou `docs/nome`.
- Commits seguem Conventional Commits: `feat:`, `fix:`, `test:`, `docs:`, `chore:`.
- Não versione `.env`, bancos, modelos, caches ou dados completos.
- Código e identificadores em inglês; interface e mensagens de produto em português.
- Mudanças em feature, regra, peso ou limiar exigem teste e atualização da documentação.

## Qualidade

Antes do pull request, execute `make lint`, `make typecheck`, `make test`, `make security` e `make build`. Descreva escopo, arquitetura, testes, impactos de segurança, limitações e screenshots quando houver UI.
