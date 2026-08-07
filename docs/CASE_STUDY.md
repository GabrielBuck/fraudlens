# Estudo de caso — FraudLens

## Contexto e problema

Alertas de pagamento perdem valor quando chegam como uma caixa-preta. A hipótese do projeto foi que regras legíveis e um detector multivariado podem se complementar, desde que a interface preserve contexto histórico, decomponha o score e mantenha uma decisão humana.

## Usuários e necessidades

- **Analista de risco:** priorizar, comparar, investigar e registrar decisão.
- **Gestor:** acompanhar volume, severidade, motivos e mudança de risco.
- **Pessoa técnica:** auditar features, fórmula, métricas, drift e arquitetura.

## Solução

Um fluxo reproduzível gera dados fictícios, injeta oito cenários, cria features causais, treina Isolation Forest, aplica regras YAML e persiste alertas. A API entrega agregações e investigação; o dashboard conduz do panorama ao evento e ao feedback.

## Decisões principais

SQLite e monólito modular reduzem atrito; PostgreSQL permanece opcional. Labels são isolados para impedir leakage. Score é prioridade, não probabilidade. Templates determinísticos oferecem explicabilidade offline. A rede é limitada para preservar performance e legibilidade.

## Resultados

Os resultados de cada execução são produzidos pelo próprio pipeline e registrados em `ModelRun` e `docs/PERFORMANCE.md`. Eles demonstram cobertura dos cenários sintéticos, não eficácia bancária real.

## Aprendizados

Explicabilidade exige modelar evidência desde o pipeline, não apenas adicionar texto ao frontend. Features temporais precisam de testes de causalidade. Segurança inclui também evitar linguagem acusatória e impedir que dados de avaliação contaminem a detecção.

## Limitações e próximos passos

Faltam calibração real, autenticação corporativa, assinatura de artefatos, processamento assíncrono e governança de feedback. A evolução natural prioriza validação temporal e controles antes de ampliar complexidade algorítmica.
