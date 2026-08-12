# Arquitetura

## Visão geral

FraudLens é um monólito modular com duas aplicações: uma API/pipeline Python e um console Next.js. SQLite reduz a barreira local; SQLAlchemy mantém a opção PostgreSQL. O design favorece rastreabilidade, reprodução e limites técnicos verificáveis.

## Contexto

```mermaid
C4Context
  title FraudLens — contexto
  Person(analyst, "Analista", "Investiga alertas e registra feedback")
  System(fraudlens, "FraudLens", "Detecta e explica anomalias sintéticas")
  System_Ext(github, "GitHub", "Código, CI e documentação")
  Rel(analyst, fraudlens, "Investiga no navegador")
  Rel(github, fraudlens, "Valida código e dependências")
```

## Containers

```mermaid
flowchart TB
  Browser[Navegador] -->|HTTP :3000| Web[Next.js]
  Web -->|JSON /api/v1| API[FastAPI]
  API --> ORM[SQLAlchemy]
  CLI[Typer CLI] --> Services[Serviços de pipeline]
  API --> Services
  Services --> ORM
  Services --> ML[scikit-learn]
  ORM --> DB[(SQLite / PostgreSQL)]
  ML --> Artifact[(joblib + JSON)]
```

## Pipeline

```mermaid
flowchart LR
  Seed[Seed + configuração] --> Gen[Gerador]
  Gen --> Quality[Validação + manifesto]
  Quality --> Raw[Entidades sintéticas]
  Raw --> Feat[Features históricas]
  Feat --> Fit[Fit Isolation Forest]
  Feat --> Rules[Regras YAML]
  Fit --> ModelScore[Score de anomalia 0–100]
  Rules --> RuleScore[Score de regras 0–100]
  ModelScore --> Combine[55/45 + intensificadores]
  RuleScore --> Combine
  Combine --> Explain[Explicação determinística]
  Explain --> Alerts[(Alertas)]
  Alerts --> Eval[Avaliação agregada com rótulos isolados]
```

## Sequência de scoring

```mermaid
sequenceDiagram
  participant C as CLI
  participant P as Pipeline
  participant F as Features
  participant M as Modelo
  participant R as Regras
  participant D as Banco
  C->>P: transactions score
  P->>D: carrega entidades ordenadas
  P->>F: calcula histórico causal
  F-->>P: matriz sem rótulos
  P->>M: score_samples
  P->>R: evaluate por transação
  P->>P: combina e explica
  P->>D: substitui alertas e atualiza ModelRun
  P-->>C: métricas reais da execução
```

## Fluxo de investigação

```mermaid
flowchart TD
  KPI[Visão geral] --> Queue[Central de alertas]
  Queue --> Case[Detalhes do alerta]
  Case --> Evidence[Evidências + composição]
  Case --> Account[Histórico da conta]
  Account --> Network[Grafo limitado]
  Evidence --> Review{Decisão humana}
  Review --> Confirm[Fraude sintética confirmada]
  Review --> False[False positive]
  Review --> Analyze[Em análise]
  Confirm --> Feedback[(Feedback)]
  False --> Feedback
  Analyze --> Feedback
```

## Banco e índices

As tabelas são `accounts`, `counterparties`, `devices`, `authentication_events`, `transactions`, `alerts`, `model_runs`, `dataset_manifests` e `alert_feedback`. Índices compostos cobrem conta/tempo, método/tempo, severidade/score e status/criação. Evidências, métricas e relatórios de qualidade usam JSON por serem documentos derivados dentro do alerta ou da execução.

## Fronteiras de operação e avaliação

`synthetic_ground_truth` e `synthetic_scenario` existem apenas na persistência e no pipeline de avaliação. Schemas Pydantic operacionais selecionam campos explicitamente e impedem que esses labels cheguem às transações, alertas, timelines ou telas de investigação. A superfície de avaliação publica somente manifesto, proveniência e métricas agregadas.

## API

Rotas públicas ficam em `/api/v1`; `/health`, `/docs` e `/redoc` são metadados operacionais. Erros de domínio seguem `{error: {code, message, details, correlation_id}}`. Paginação tem limite 100. Endpoints administrativos existem, mas respondem como indisponíveis até `ENABLE_ADMIN_API=true` e exigem comparação constante do token de ambiente.

## Frontend

O App Router renderiza dados no servidor para a primeira carga. Mutações de revisão são client-side. Recharts atende séries e distribuições; React Flow limita e explora a rede. Componentes comunicam severidade com texto e cor, preservam foco visível e respeitam redução de movimento.

## Decisões e trade-offs

- **Monólito modular em vez de microserviços:** menor custo operacional e melhor demonstrabilidade; módulos permitem futura extração.
- **SQLite padrão:** execução em um comando; PostgreSQL é perfil opcional para discutir concorrência.
- **Batch em vez de streaming:** reprodução determinística e local; produção exigiria eventos, idempotência e filas.
- **Features calculadas em pandas:** transparência; alto volume exigiria SQL/warehouse ou engine distribuída.
- **Joblib local:** suficiente para artefato gerado localmente; produção exige registry, assinatura e armazenamento imutável.
- **Explicação por template:** auditável e offline; um LLM seria apenas enriquecimento controlado, nunca requisito.

## Alternativas rejeitadas

Não foram adotados Kafka, Kubernetes, feature store, autenticação corporativa ou APIs de IA porque adicionariam complexidade sem melhorar o objetivo do MVP. Um modelo supervisionado foi rejeitado por não haver rótulos reais; os rótulos sintéticos permanecem exclusivos da avaliação.

## Evolução para produção

Separar ingestão e scoring, materializar features com contratos, adicionar autenticação e RBAC, assinar artefatos, criar auditoria append-only, calibrar limiares temporalmente, testar fairness com base legal adequada, implantar rate limit distribuído e observabilidade OpenTelemetry.
