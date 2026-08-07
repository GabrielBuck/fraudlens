# Post para LinkedIn

## Versão principal — recomendada

Como transformar um alerta técnico em algo que realmente ajude alguém a investigar?

Essa pergunta foi o ponto de partida do FraudLens.

Eu queria construir mais do que um modelo que devolvesse um número. Por isso, desenvolvi um fluxo completo: geração de pagamentos sintéticos, features históricas sem olhar o futuro, Isolation Forest, regras explicáveis, risk score, API e um dashboard para investigação humana.

O resultado conecta três perguntas que considero essenciais:

- O que aconteceu?
- Por que este evento foi sinalizado?
- Qual contexto uma pessoa precisa antes de decidir?

Na execução documentada, o pipeline processou 50.000 transações sintéticas e oito cenários controlados. Obteve recall de 93% e PR-AUC de 0,8523, com precision de 13,22%. Esses números pertencem exclusivamente ao experimento sintético — não representam desempenho bancário real. A menor precision também deixa visível um trade-off importante: priorizar recall aumenta o volume que precisa de revisão.

Ao longo do projeto, trabalhei engenharia de dados causal, machine learning não supervisionado, FastAPI, Next.js, segurança, testes automatizados e validação Docker. Mais importante do que listar tecnologias foi conectá-las em uma experiência coerente, rastreável e honesta sobre seus limites.

Meu maior aprendizado foi que explicabilidade não é um texto colocado depois do score. Ela começa na forma como os dados são construídos, passa pelas regras e termina na interface usada para investigar.

Código, arquitetura, resultados e documentação:
https://github.com/GabrielBuck/fraudlens

#MachineLearning #DataEngineering #SoftwareEngineering #CyberSecurity #Tech

## Versão curta

Como transformar um alerta técnico em algo que realmente ajude alguém a investigar?

Foi dessa pergunta que nasceu o FraudLens: uma plataforma full stack que gera pagamentos sintéticos, constrói features sem vazamento temporal, combina Isolation Forest com regras explicáveis e apresenta cada sinal em uma interface de investigação.

Na execução documentada, foram 50.000 transações sintéticas, recall de 93% e PR-AUC de 0,8523. A precision foi 13,22%, deixando explícito o trade-off de priorizar recall. São resultados de cenários 100% sintéticos, não expectativa de produção.

O maior aprendizado foi integrar dados, ML, backend, frontend e segurança em torno de uma decisão humana — e documentar honestamente os limites.

https://github.com/GabrielBuck/fraudlens

#MachineLearning #DataEngineering #SoftwareEngineering #CyberSecurity

## Versão técnica

O FraudLens nasceu de uma restrição: como demonstrar detecção de anomalias sem dados reais e sem deixar que os rótulos sintéticos contaminem o modelo?

O pipeline gera entidades e pagamentos determinísticos, ordena os eventos no tempo e calcula 40 features com janelas fechadas à esquerda. `synthetic_ground_truth` e `synthetic_scenario` ficam isolados da matriz de treino e entram apenas na avaliação.

Um Isolation Forest não supervisionado produz o componente de anomalia. Um motor YAML com 13 regras adiciona sinais legíveis. O score final combina modelo e regras para ordenar a fila; não é probabilidade nem prova de fraude. Cada alerta preserva a decomposição, as evidências e uma explicação determinística.

FastAPI, SQLAlchemy e Alembic sustentam API e persistência; Next.js apresenta overview, alertas, conta, rede e monitoramento. Ruff, mypy, pytest, ESLint, Vitest, Playwright, audits, CodeQL e Docker CI validam as fronteiras técnicas.

Na base documentada de 50.000 transações e prevalência positiva sintética de 0,8%, o sistema alcançou recall 0,93, precision 0,1322, F1 0,2315 e PR-AUC 0,8523. O resultado evidencia o trade-off de uma configuração orientada a recall e não deve ser extrapolado para produção.

Arquitetura e código:
https://github.com/GabrielBuck/fraudlens

#MachineLearning #DataEngineering #SoftwareEngineering #CyberSecurity
