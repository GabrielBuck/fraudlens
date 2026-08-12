# Model Card — FraudLens Isolation Forest

## Objetivo e uso pretendido

Ordenar pagamentos sintéticos por prioridade de investigação e demonstrar a integração entre features causais, modelo não supervisionado, regras e explicabilidade. Não é apropriado para bloqueio, acusação, decisão sobre clientes ou estimativa de probabilidade real de fraude.

## Dados

O gerador determinístico cria perfis empresariais fictícios e injeta oito comportamentos controlados. Não há PII. `synthetic_ground_truth` e `synthetic_scenario` só entram após o scoring para avaliação. Um teste falha se algum rótulo aparecer em `MODEL_FEATURES`.

## Features

Valores e log, estatísticas históricas, z-score, razão para média, ciclo temporal, janelas 5m/30m/1h/24h, negações, recorrência de contraparte e método, dispositivo, Haversine, velocidade geográfica, perfil da conta e proporção de saídas. Janelas são fechadas à esquerda; o evento atual e o futuro não compõem sua referência.

## Algoritmo e treinamento

Pipeline: imputação pela mediana, `RobustScaler` e `IsolationForest(n_estimators=180, contamination=0.08, random_state=seed)`. O modelo é treinado em todas as linhas sem rótulo e salvo junto à ordem das features, seed e parâmetros. A execução persiste também hash do dataset, assinatura das features, versão do código e SHA-256 do artefato.

## Score

O valor de `score_samples` é invertido e mapeado entre os percentis 1 e 99 observados no treino:

```text
model_score = clip((raw_p99 - raw) / (raw_p99 - raw_p01) × 100, 0, 100)
final = clip(model_score × 0,55 + rules_score × 0,45 + booster, 0, 100)
```

Boosters acrescentam oito pontos quando combinações críticas de regras coexistem. Um alerta é persistido quando o score final alcança 30 e existe score de regras ≥ 18 ou anomalia extrema do modelo ≥ 95. O score é prioridade, não probabilidade.

## Avaliação

São calculados precision, recall, F1, PR-AUC, Precision@K, Recall@K, matriz de confusão, recall por cenário, alert rate e false positive rate. Resultados variam com seed e volume e são válidos somente no conjunto sintético da execução.

## Limitações e riscos

- Cenários programados simplificam a diversidade de fraude real.
- Contamination e limiar de alerta são heurísticos.
- Drift usa PSI e estatísticas simples, sem causalidade.
- Um atacante que conheça regras pode adaptar o comportamento.
- O joblib só deve carregar artefato criado pelo próprio pipeline.
- Segmento empresarial não é atributo protegido, mas qualquer uso real exigiria avaliação de impacto e fairness.

## Reprodutibilidade

Registre seed, hash do conjunto, versão do código, parâmetros, features e timestamp do `ModelRun`. A mesma seed e contagens produzem as mesmas entidades e transações; o modelo usa `random_state` fixo.

## Melhorias futuras

Validação temporal, calibração de score, ensembles, explicações locais por feature, registry assinado, detecção de drift por feature e aprendizado ativo governado pelo feedback.
