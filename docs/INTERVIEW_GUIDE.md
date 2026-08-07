# Guia para entrevistas

## Pitch de 30 segundos

“FraudLens é uma plataforma full stack que gera pagamentos sintéticos, detecta anomalias com Isolation Forest e regras configuráveis, explica cada alerta e oferece uma investigação visual. O projeto demonstra dados, ML, backend, frontend e segurança sem usar PII ou APIs pagas.”

## Pitch de 90 segundos

Explique o problema da caixa-preta, os oito cenários, features causais, combinação 55/45, API, dashboard e feedback. Termine com: “o score ordena trabalho; a decisão continua humana”.

## Explicação de 3 minutos

Percorra arquitetura, causalidade, reprodução por seed, ausência de target leakage, métricas sintéticas, threat model e trade-off monólito/SQLite. Mostre uma limitação e como mudaria em produção.

## Perguntas técnicas prováveis

**Por que Isolation Forest?** Não exige rótulo operacional, funciona bem como baseline multivariado e oferece interface de score. Não implica que seja o melhor modelo para produção.

**Como evitou leakage?** Ordenação por conta/tempo/id, `shift(1)`, rolling fechado à esquerda e rótulos fora da lista de features, com testes dedicados.

**Por que combinar regras e modelo?** Regras são auditáveis e precisas para padrões conhecidos; o modelo encontra combinações raras. A decomposição permite entender a contribuição de cada um.

**O score é probabilidade?** Não. É um índice de prioridade calibrado apenas para ordenar investigação.

**Como avaliou sem fraude real?** Labels injetados medem se o pipeline encontra os cenários que ele mesmo controla. Isso valida integração/metodologia, não generalização real.

**Como lidaria com escala?** Materializaria features em warehouse/stream, scoring assíncrono idempotente, Postgres/OLAP, cache distribuído e observabilidade com tracing.

**Quais riscos de segurança?** Admin exposto, poisoning, evasão, adulteração de artefato e interpretação indevida. Threat model documenta controles e lacunas.

## O que seria diferente em produção

SSO/RBAC, TLS, secrets manager, audit log, registry assinado, validação temporal, processo de aprovação de regras, experimentação shadow, revisão de fairness, SLAs e resposta a incidentes.
