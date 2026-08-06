# Performance

Medição realizada em 6 de agosto de 2026 no runtime local do Codex, Windows, Python 3.12, Node 24, SQLite e processamento em um único processo. Cada endpoint foi chamado três vezes com a base já carregada; os tempos incluem serialização HTTP local.

## Base padrão

| Item | Resultado medido |
|---|---:|
| Contas | 1.000 |
| Transações | 50.000 |
| Cenários | 8 tipos, 400 linhas positivas |
| Alertas persistidos | 2.814 |
| Hash do conjunto | `8c84033ed56d2bdb` |
| Seed | 42 |

## Pipeline

| Etapa | Tempo |
|---|---:|
| Geração e persistência | 3,492 s |
| Features + treinamento | 36,662 s |
| Features + regras + scoring | 40,344 s |
| Fluxo completo | 83,104 s |

## Endpoints

| Endpoint | Média | Mínimo | Máximo |
|---|---:|---:|---:|
| `/health` | 37,75 ms | 1,40 ms | 109,70 ms |
| `/api/v1/overview` | 153,39 ms | 144,11 ms | 165,81 ms |
| `/api/v1/alerts?page_size=20` | 9,93 ms | 8,29 ms | 12,52 ms |
| `/api/v1/model-monitoring` | 924,62 ms | 874,46 ms | 955,32 ms |

## Métricas sintéticas da execução

Recall `0,93`, precision `0,1322`, F1 `0,2315`, Precision@K `0,8175`, Recall@K `0,8175`, PR-AUC `0,8523`, alert rate `0,0563` e false positive rate `0,0492`.

A baixa prevalência injetada (0,8%) torna precision sensível a falsos positivos. O sistema prioriza recall e ordenação; as métricas não representam produção e não devem ser comparadas diretamente a soluções financeiras reais.

## Leitura e limitações

Alertas e listagem atendem confortavelmente à demonstração local. O monitoramento ainda varre transações para comparar janelas e é o endpoint mais caro; em produção, estatísticas seriam materializadas e armazenadas por execução. O benchmark não mede concorrência, rede externa, PostgreSQL ou containerização porque Docker não estava disponível no ambiente de validação.
