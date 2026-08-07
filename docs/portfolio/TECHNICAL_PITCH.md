# Pitch técnico

## 30 segundos

FraudLens é um monólito modular com pipeline Python e dashboard Next.js. Ele gera pagamentos sintéticos determinísticos, calcula 40 features causais, combina Isolation Forest com 13 regras YAML, persiste alertas explicáveis e os expõe por uma API FastAPI. O score ordena prioridade de investigação; não é probabilidade. A solução é testada, auditada e validada em Docker CI.

## 2 minutos

O FraudLens demonstra um fluxo completo de investigação de anomalias sem depender de dados reais. A geração é determinística por seed e injeta oito cenários sintéticos. Antes do scoring, as transações são ordenadas por timestamp e as features históricas usam janelas fechadas à esquerda, impedindo que o evento atual ou o futuro entrem na referência.

A matriz de 40 features passa por imputação mediana, `RobustScaler` e `IsolationForest` com `random_state` fixo. Em paralelo, um motor avalia 13 regras configuradas em YAML. O score final combina 55% do componente do modelo, 45% do componente de regras e boosters contextuais. Alertas só são persistidos quando há prioridade mínima e evidência suficiente de regra ou anomalia extrema. O score é uma ordenação operacional, não uma probabilidade.

FastAPI expõe rotas versionadas e serviços de domínio sobre SQLAlchemy e Alembic. SQLite reduz a barreira local e PostgreSQL permanece opcional. O frontend Next.js oferece overview, fila, detalhes, histórico de conta, rede, cenários e monitoramento do modelo.

No experimento documentado, 50.000 transações sintéticas resultaram em recall 0,93, precision 0,1322, F1 0,2315 e PR-AUC 0,8523. A prevalência positiva é 0,8%, e o trade-off de falsos positivos é explicitamente documentado.

## 5 minutos

### Problema

Uma fila de pagamentos pode conter milhares de padrões legítimos e poucos eventos que merecem contexto adicional. Um score isolado não explica o que mudou nem ajuda a revisar evidências. O FraudLens trata detecção como priorização para investigação humana.

### Arquitetura

A solução é um monólito modular com dois processos principais: pipeline/API em Python e interface Next.js. Os módulos separam geração, features, detecção, serviços, persistência e apresentação. Essa escolha reduz complexidade operacional no MVP e mantém fronteiras que poderiam ser extraídas no futuro.

### Dados

O gerador cria contas empresariais, contrapartes, dispositivos, autenticações e pagamentos fictícios. Oito cenários controlados produzem 400 linhas positivas em 50.000 transações. Seed, hash do conjunto e parâmetros são registrados para reprodução. Não há PII.

### Features

São 40 variáveis de valor, frequência, janelas temporais, recorrência, dispositivo, método, contraparte, geografia e perfil. Os eventos são ordenados e as janelas são fechadas à esquerda. Assim, cada linha usa apenas dados estritamente anteriores ao seu timestamp. Um teste impede que `synthetic_ground_truth` ou `synthetic_scenario` apareçam em `MODEL_FEATURES`.

### Modelo

O pipeline usa imputação mediana, `RobustScaler` e `IsolationForest(n_estimators=180, contamination=0.08, random_state=seed)`. A escolha não supervisionada é coerente com a ausência de rótulos reais. O valor de `score_samples` é invertido e normalizado pelos percentis 1 e 99 do treino para formar um componente de 0 a 100.

### Regras

Treze regras YAML representam sinais legíveis, como dispositivo novo, valor atípico, velocidade e deslocamento incompatível. Elas preservam valor observado, referência e reason code. O objetivo é complementar o modelo com conhecimento explicitável, não simular certeza.

### Scoring

O score final usa 55% do modelo, 45% das regras e boosters quando sinais críticos coexistem. A persistência exige score final mínimo e também evidência suficiente de regra ou anomalia extrema. O resultado é prioridade de investigação; não é probabilidade de fraude.

### API

FastAPI organiza endpoints sob `/api/v1`, com paginação limitada, filtros, erros de domínio padronizados e correlation ID. SQLAlchemy parametriza o acesso e Alembic versiona o banco. Endpoints administrativos ficam desabilitados por padrão e exigem token de ambiente quando habilitados.

### Frontend

Next.js e React apresentam KPIs, central de alertas, decomposição do score, evidências, histórico da conta, rede, métricas e cenários. Recharts e React Flow apoiam as visualizações. A interface usa texto além de cor, foco visível e estados de carregamento, vazio e erro.

### Segurança

O projeto usa apenas dados sintéticos, restringe CORS, valida entradas, evita logar payloads sensíveis e mantém secrets fora do repositório. `pip-audit`, `npm audit`, CodeQL, Dependabot e revisão de arquivos versionados cobrem riscos de dependência e código. O threat model documenta riscos residuais.

### Resultados

Na execução documentada: recall 0,93, precision 0,1322, F1 0,2315, PR-AUC 0,8523, Precision@K e Recall@K 0,8175, alert rate 0,0563 e false positive rate 0,0492. Foram persistidos 2.814 alertas. Tudo foi medido em cenários sintéticos.

### Limitações

O gerador simplifica a diversidade do mundo real; contamination e limiares são heurísticos; o batch local não representa streaming; e não há autenticação corporativa, fairness validada nem observabilidade de produção. Uma evolução real exigiria validação temporal, dados governados, calibração, RBAC, auditoria imutável, monitoramento e revisão de impacto.
