# Pitch para recrutadores

## 15 segundos

O FraudLens é uma plataforma full stack que transforma pagamentos sintéticos em sinais de risco explicáveis, conectando engenharia de dados, machine learning, software, segurança e investigação humana.

## 30 segundos

Eu criei o FraudLens para responder a uma pergunta: como transformar um alerta técnico em algo que uma pessoa realmente consiga investigar? O projeto gera pagamentos sintéticos, identifica comportamentos atípicos, explica os sinais e os apresenta em um dashboard. O diferencial é integrar dados, machine learning, backend, frontend, segurança e testes em uma única solução reproduzível.

## 60 segundos

O FraudLens é um projeto de portfólio full stack para investigação de anomalias em pagamentos sintéticos. Em vez de parar em um score de machine learning, ele percorre o fluxo completo: gera dados fictícios, constrói histórico sem usar informações futuras, combina um modelo não supervisionado com regras explicáveis, disponibiliza uma API e apresenta os alertas em um dashboard para revisão humana.

Na execução documentada, o sistema processou 50.000 transações sintéticas e alcançou recall de 93% nos cenários controlados. Esse resultado não representa produção; ele ajuda a discutir trade-offs, porque a configuração orientada a recall também produziu precision de 13,22%.

O maior aprendizado foi transformar várias disciplinas em uma experiência coerente e comunicar tanto os resultados quanto os limites com clareza.

## 90 segundos

O problema que escolhi não foi apenas “detectar fraude”. Foi entender como um sistema pode organizar sinais de risco para que uma pessoa investigue melhor, sem tratar um score como prova.

Por isso, construí o FraudLens de ponta a ponta. Ele gera contas e pagamentos totalmente fictícios, cria features históricas sem olhar o futuro, usa Isolation Forest para encontrar padrões isolados e combina esse resultado com 13 regras explicáveis. Cada alerta preserva os motivos, o contexto e a composição do risk score. Uma API FastAPI e um dashboard Next.js permitem navegar da visão executiva para o evento, a conta e a rede de relacionamentos.

Também tratei o projeto como produto de software: banco versionado, validação de entradas, documentação de segurança, testes, coverage, auditoria de dependências, CodeQL e Docker CI.

Na base sintética documentada, foram 50.000 transações, recall de 93% e PR-AUC de 0,8523. A precision de 13,22% mostra o custo da priorização de recall e abre uma boa conversa sobre falsos positivos. Eu não apresento esses números como desempenho bancário real.

O diferencial do projeto é justamente essa integração: dados, ML, engenharia de software, segurança e pensamento de produto em torno de uma decisão humana.
