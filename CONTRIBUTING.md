# Contribuindo

## Ambiente local

Use `scripts/setup.ps1` no Windows ou `scripts/setup.sh` no macOS/Linux. Inicialize o banco e
execute `fraudlens pipeline run-all` antes de iniciar a API e a interface.

## Convenções

- Crie branches curtas a partir de `main` e use Conventional Commits.
- Código, identificadores e comentários técnicos são escritos em inglês; interface, respostas da
  API e documentação principal usam português brasileiro.
- Rotas da API ficam em `/api/v1`; saúde permanece em `/health`.
- Endpoints de lista usam paginação limitada e ordenação estável.
- Erros de domínio são explícitos e entradas externas são validadas.
- Não versione `.env`, credenciais, bancos, artefatos de modelo, caches, logs, cobertura ou bases
  sintéticas completas.

## Dados, detecção e segurança

- Toda entidade é fictícia. Não adicione PII, CPF, CNPJ ou identificadores pessoais realistas.
- Features históricas só podem usar eventos estritamente anteriores ao timestamp da linha.
- `synthetic_ground_truth` e `synthetic_scenario` pertencem exclusivamente à avaliação. Eles não
  podem entrar em features nem contratos operacionais da API.
- O score expressa prioridade de investigação; nunca probabilidade ou prova de fraude.
- Toda alteração em regra, feature, peso, limiar ou fórmula exige teste focado e documentação.
- Explicações são determinísticas, neutras e não acusatórias.
- Endpoints administrativos permanecem desabilitados por padrão e exigem token via ambiente.

## Qualidade e documentação

Registre decisões materiais de arquitetura, scoring, segurança e produto em `docs/`. Publique
somente métricas efetivamente medidas e identifique sempre o contexto sintético. Mudanças de UI
devem incluir estados de carregamento, vazio e erro, navegação por teclado e revisão responsiva.

Antes do pull request, execute `make lint`, `make typecheck`, `make test`, `make security` e
`make build`. Descreva escopo, testes, impacto de segurança, limitações e screenshots quando houver
alteração visual.
