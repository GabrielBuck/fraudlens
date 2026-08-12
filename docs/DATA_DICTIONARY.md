# Dicionário de dados

## Entidades

| Tabela | Chave | Conteúdo |
|---|---|---|
| `accounts` | `ACC-000001` | Segmento, cidade-base, idade, janela habitual e volume esperado |
| `counterparties` | `CP-000001` | Categoria, localidade, recorrência e risco histórico sintético |
| `devices` | `DEV-000001` | Conta, primeira/última observação, plataforma e confiança |
| `authentication_events` | `AUTH-00000001` | Resultado, timestamp, dispositivo, IP/localidade e motivo de falha |
| `transactions` | `TX-00000001` | Conta, contraparte, dispositivo, valor, método, direção, status e localização |
| `alerts` | `ALT-00000001` | Scores, severidade, motivos, explicação, evidência e revisão |
| `model_runs` | `RUN-*` | Parâmetros, features, volumes, métricas e artefato |
| `dataset_manifests` | `DST-*` | Seed, schema, intervalo, contagens, hash e validações de integridade |
| `alert_feedback` | `FDB-*` | Classificação, comentário e timestamp da decisão humana |

Todos os timestamps são UTC/timezone-aware na aplicação. Valores são BRL fictícios. Estados de alerta: `novo`, `em análise`, `fraude confirmada`, `falso positivo`, `encerrado`. Severidades: `baixa`, `média`, `alta`, `crítica`.

## Features do modelo

- **Valor:** `amount`, `amount_log`, `historical_mean`, `historical_median`, `historical_std`, `amount_zscore`, `amount_to_mean_ratio`.
- **Tempo:** seno/cosseno de hora e dia, fim de semana, horário incomum, minutos desde anterior.
- **Velocidade:** contagens 5m/30m/1h/24h, somas 1h/24h, negações e falhas de autenticação.
- **Relacionamento:** contraparte nova, distintas 24h, frequência e risco histórico.
- **Dispositivo/local:** novo/confiável, dispositivos 24h, distâncias, velocidade, cidade/país novos.
- **Canal/conta:** frequência e novidade do método, taxa de negação, idade, volume mensal e proporção de saídas.

`synthetic_ground_truth` e `synthetic_scenario` são rótulos de avaliação: nunca entram em features nem em contratos operacionais da API. A interface operacional recebe somente dados permitidos por schemas explícitos.

O campo `context_booster` do alerta registra separadamente a contribuição contextual. `ModelRun` registra seed, hash do dataset, assinatura ordenada das features, versão do código e hash do artefato.

## Regras de causalidade

Ordenação estável por conta/timestamp/id, `shift(1)` para estatísticas, rolling `closed="left"` e conjuntos incrementais atualizados somente depois de calcular a linha atual.
