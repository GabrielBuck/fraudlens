# Performance

Medição final da v1 realizada em 12 de agosto de 2026 em ambiente local Windows, Python 3.12, Node 24, SQLite e processamento em um único processo. Cada endpoint foi aquecido e chamado cinco vezes com a base já carregada; os tempos incluem serialização HTTP local via `TestClient`.

## Base padrão

| Item | Resultado medido |
|---|---:|
| Contas | 1.000 |
| Transações | 50.000 |
| Cenários | 8 tipos, 400 linhas positivas |
| Alertas persistidos | 2.814 |
| Hash SHA-256 do conjunto | `8595bb1f1ea15780de0a5a5509c176fb679fcc9819f4076f421f8f9a1e1d3614` |
| Seed | 42 |

## Pipeline

| Etapa | Tempo |
|---|---:|
| Geração, validação, manifesto e persistência | 3,656 s |
| Features + treinamento | 36,393 s |
| Features + regras + scoring | 41,123 s |
| Fluxo completo (soma das etapas) | 81,172 s |

## Endpoints

| Endpoint | Média | Mínimo | Máximo |
|---|---:|---:|---:|
| `/health` | 3,49 ms | 2,76 ms | 4,96 ms |
| `/api/v1/overview` | 284,17 ms | 275,86 ms | 291,01 ms |
| `/api/v1/alerts?page_size=20` | 10,85 ms | 6,96 ms | 19,14 ms |
| `/api/v1/model-monitoring` | 4,77 ms | 4,00 ms | 5,66 ms |

## Métricas sintéticas da execução

Recall `0,93`, precision `0,1322`, F1 `0,2315`, Precision@K `0,8175`, Recall@K `0,8175`, PR-AUC `0,8523`, alert rate `0,0563` e false positive rate `0,0492`.

A baixa prevalência injetada (0,8%) torna precision sensível a falsos positivos. O sistema prioriza recall e ordenação; as métricas não representam produção e não devem ser comparadas diretamente a soluções financeiras reais.

## Leitura e limitações

O monitoramento caiu de um baseline anterior de `924,62 ms` para `4,77 ms` ao mover o cálculo para a etapa de scoring e ler indicadores materializados do `ModelRun` (redução observada de aproximadamente 99,5% neste ambiente). O overview ficou mais caro que o baseline anterior porque agora aplica período real, calcula a janela anterior equivalente e consulta contagens operacionais consistentes; as agregações foram consolidadas para limitar o custo.

O benchmark não mede concorrência, rede externa, PostgreSQL ou performance em containers. Validações de CI e smoke tests não são benchmarks. Recall `0,93` e PR-AUC `0,8523` pertencem exclusivamente aos 400 exemplos positivos dos cenários sintéticos desta execução.
