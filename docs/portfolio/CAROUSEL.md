# Carrossel FraudLens

## Lógica narrativa

O carrossel segue o caminho que uma pessoa faria ao avaliar o projeto: primeiro entende a promessa, depois reconhece o problema, acompanha o funcionamento, vê a experiência de investigação, compreende a arquitetura, confere os resultados e encerra com o aprendizado. A narrativa evita começar por bibliotecas; tecnologia aparece como meio para transformar dados em uma decisão humana mais informada.

## Slide 1 — Capa

**Objetivo:** interromper a rolagem e posicionar o projeto em poucos segundos.

**Mensagem principal:** FraudLens — Intelligent Payment Anomaly Radar.

**Elemento visual:** radar autoral, recorte real do dashboard e assinatura cromática ciano/roxo.

**Texto:** “Do pagamento ao sinal. Do sinal à explicação.” e “Dados + Machine Learning + Software + Segurança”.

**O que explicar se alguém perguntar:** o projeto cobre o caminho completo entre dados sintéticos, detecção, API, dashboard e revisão humana; não é apenas um notebook de ML.

## Slide 2 — O problema

**Objetivo:** explicar por que um score isolado não resolve uma investigação.

**Mensagem principal:** um score sozinho não explica uma anomalia.

**Elemento visual:** funil de 50.000 pagamentos para sinais priorizados, cercado pelos contextos analisados.

**Texto:** volume, histórico, dispositivo, horário, localização, contraparte e velocidade convergem para a pergunta “o que merece atenção?”.

**O que explicar se alguém perguntar:** o desafio não é acusar ou bloquear; é reduzir o espaço de busca e reunir contexto para uma pessoa investigar.

## Slide 3 — Como funciona

**Objetivo:** mostrar o pipeline sem transformar o slide em um diagrama de infraestrutura.

**Mensagem principal:** dados viram prioridade de investigação por meio de features causais, modelo e regras.

**Elemento visual:** fluxo de pagamentos sintéticos até explicação, com uma bifurcação entre Isolation Forest e 13 regras explicáveis.

**Texto:** 40 features, 13 regras, 1 modelo não supervisionado.

**O que explicar se alguém perguntar:** o modelo encontra isolamento multivariado; as regras expressam sinais de domínio; o score combina ambos e não é probabilidade de fraude.

## Slide 4 — Investigação

**Objetivo:** provar que o resultado é investigável, não apenas calculado.

**Mensagem principal:** cada alerta precisa responder o que aconteceu, por que foi sinalizado e o que mudou.

**Elemento visual:** screenshots reais de perfil da conta e grafo de relacionamentos, com chamadas para histórico, dispositivo, contraparte e timeline.

**Texto:** “Contexto antes da conclusão” e cinco perguntas investigativas.

**O que explicar se alguém perguntar:** a aplicação permite sair da fila, ler evidências, navegar pelo histórico e pela rede e registrar feedback humano.

## Slide 5 — Arquitetura

**Objetivo:** demonstrar amplitude full stack e decisões pragmáticas.

**Mensagem principal:** uma única solução conecta geração, scoring, persistência, API e interface.

**Elemento visual:** diagrama em camadas do dado sintético ao dashboard, com a base de qualidade abaixo.

**Texto:** Full-stack, reprodutível, containerizado e testado.

**O que explicar se alguém perguntar:** é um monólito modular deliberado; reduz custo operacional para o MVP sem misturar limites de dados, domínio, API e UI.

## Slide 6 — Resultados

**Objetivo:** apresentar evidências reais sem transformar um experimento sintético em claim comercial.

**Mensagem principal:** os números demonstram o comportamento da execução documentada.

**Elemento visual:** cards numéricos com recall e PR-AUC em destaque, acompanhados de precision e F1 para explicitar o trade-off.

**Texto:** 1.000 contas, 50.000 transações, 8 cenários, recall 93%, PR-AUC 0,8523, precision 13,22%, F1 0,2315 e 2.814 alertas.

**O que explicar se alguém perguntar:** o sistema foi configurado para priorizar recall em uma base positiva de aproximadamente 0,8%; por isso há mais falsos positivos e a precision é menor. Todos os cenários são sintéticos.

## Slide 7 — Encerramento

**Objetivo:** fechar com maturidade e direcionar para o GitHub.

**Mensagem principal:** o maior aprendizado não foi um algoritmo; foi conectar tecnologia a uma decisão.

**Elemento visual:** seis áreas orbitando a revisão humana, com CTA discreto.

**Texto:** Data Engineering, Machine Learning, Backend, Frontend, Security e Product Thinking.

**O que explicar se alguém perguntar:** a qualidade do projeto vem das conexões entre disciplinas, dos limites documentados e da responsabilidade na apresentação dos resultados.
