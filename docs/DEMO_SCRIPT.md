# Roteiro de demonstração — 3 a 5 minutos

## 0:00 — Introdução

“FraudLens transforma pagamentos sintéticos em alertas explicáveis. O foco é priorizar investigação, nunca afirmar culpa.”

## 0:30 — Visão geral

Mostre volume, transações, alertas e severidade. Explique que os cards e gráficos vêm da API e da base gerada pela seed.

## 1:10 — Alerta crítico

Abra a central, filtre “crítica” e escolha um caso. Destaque score final, modelo, regras e intensificador. Leia a explicação neutra.

## 2:00 — Evidência e linha do tempo

Mostre valores observados/esperados, evento atual e operações próximas. Navegue para a conta e compare valor, janela horária e meios recorrentes.

## 2:50 — Grafo

Abra a rede, use zoom/pan e a legenda. Explique o limite de nós e o destaque de risco.

## 3:20 — Modelo

Apresente F1, matriz, recall por cenário e PSI. Reforce: rótulos são sintéticos e não entram no treino.

## 4:00 — Arquitetura e encerramento

Mostre o diagrama: geração → features → modelo/regras → score → API → dashboard. Registre uma revisão e conclua com as limitações e próximos passos de produção.
