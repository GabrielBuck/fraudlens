# Interview Cheatsheet

Respostas curtas para orientar conversas. Adapte a profundidade ao interlocutor; não memorize como roteiro rígido.

## Machine Learning

### Por que Isolation Forest?

Porque o projeto não possui rótulos reais confiáveis. O algoritmo identifica observações isoladas em um espaço multivariado, funciona bem como baseline não supervisionado e oferece treinamento local reproduzível.

### Por que não usar classificação supervisionada?

Treinar com os rótulos programados pelo próprio gerador mediria a capacidade de reproduzir a simulação e aumentaria o risco de target leakage. Em um caso real, classificação exigiria histórico rotulado, qualidade de labels, validação temporal e governança.

### O que significa não supervisionado?

O modelo aprende a estrutura dos dados sem receber a resposta “fraude” ou “normal” durante o treino. Os rótulos sintéticos são usados somente depois, para avaliar a ordenação produzida.

### Como funciona Isolation Forest?

Ele cria árvores com cortes aleatórios. Pontos que precisam de menos cortes para ficar isolados têm comportamento mais incomum. A média do caminho de isolamento gera um score relativo de anomalia.

### O que significa recall?

Entre os cenários positivos conhecidos na avaliação, recall mede qual proporção foi sinalizada. Recall 0,93 significa que 93% das linhas positivas sintéticas foram recuperadas.

### O que significa precision?

Entre os alertas gerados, precision mede qual proporção corresponde às linhas positivas da avaliação sintética. Ela responde a uma pergunta diferente de recall.

### Por que recall 93% e precision 13,22%?

A base tem prevalência positiva de aproximadamente 0,8% e o sistema foi configurado para priorizar recall. Isso recupera a maioria dos cenários, mas inclui muitos falsos positivos. O resultado é útil para discutir custo de revisão, não para esconder o trade-off.

### Por que PR-AUC é relevante?

Em classes raras, accuracy e ROC-AUC podem parecer boas mesmo com uma fila pouco útil. PR-AUC resume o equilíbrio entre precision e recall ao variar o limiar e é mais informativa para o cenário desbalanceado.

### Como reduzir falsos positivos?

Com validação temporal, limiares segmentados, melhores features históricas, regras ajustadas com feedback revisado, calibração por capacidade operacional e avaliação do custo de cada tipo de erro.

### O score é probabilidade de fraude?

Não. É uma prioridade relativa formada por score do modelo, score das regras e intensificadores. Probabilidade exigiria calibração e validação com rótulos reais representativos.

### Como validar isso em produção?

Com shadow mode, backtesting temporal, amostra revisada por especialistas, métricas por segmento, capacidade da fila, custo de falsos positivos e falsos negativos, drift, fairness, testes de estabilidade e rollout gradual.

## Dados

### O que é data leakage?

É usar, durante treino ou scoring, informação que não estaria disponível no momento real da decisão. Isso infla métricas e reduz validade operacional.

### Como foi evitado?

As transações são ordenadas por timestamp e as janelas históricas são fechadas à esquerda. O evento atual e os eventos futuros não entram na referência daquela linha.

### O que é target leakage?

É quando o rótulo ou uma variável que revela diretamente o rótulo entra nas features. Aqui, `synthetic_ground_truth` e `synthetic_scenario` são exclusivos da avaliação e um teste impede seu uso em `MODEL_FEATURES`.

### Como as features temporais foram construídas?

Com grupos por conta e outras entidades, ordenação estável e estatísticas acumuladas ou em janelas de 5 minutos a 24 horas que usam somente observações anteriores.

### Por que usar seed?

A seed fixa as escolhas pseudoaleatórias do gerador e do modelo, permitindo repetir entidades, transações e resultados para depuração, testes e comparação.

### Como garantir reprodutibilidade?

Registrando seed, hash do conjunto, volume, parâmetros, ordem das features, versão do código e timestamp da execução. Dependências e migrações também são versionadas.

## Software

### Por que FastAPI?

Oferece tipagem, validação com Pydantic, documentação OpenAPI e baixo atrito para uma API Python que compartilha contratos com o domínio de dados.

### Por que Next.js?

O App Router permite primeira carga no servidor, rotas organizadas e componentes React para investigação interativa. TypeScript estrito protege contratos na interface.

### Por que um monólito modular?

É a menor arquitetura que demonstra o fluxo completo com execução local simples. Os limites internos permanecem claros, sem o custo operacional de microserviços prematuros.

### Como a API está organizada?

Rotas ficam sob `/api/v1`, chamam serviços de domínio e usam repositórios SQLAlchemy. Há paginação limitada, filtros, erros padronizados e endpoints operacionais separados.

### Como escalaria?

Separaria ingestão, feature computation e scoring; materializaria features; adotaria filas idempotentes, PostgreSQL/warehouse conforme acesso, cache e observabilidade. A extração seria guiada por gargalos medidos.

## Segurança

### Como secrets são tratados?

Somente por variáveis de ambiente. `.env` é ignorado, `.env.example` não contém segredo real, e os workflows não dependem de credenciais da aplicação.

### Qual é o threat model?

Ele cobre exposição de dados, abuso de endpoints, dependências, artefatos de modelo, logs, CORS, disponibilidade e manipulação de feedback, com controles e riscos residuais documentados.

### Quais riscos permanecem?

Rate limiting é local, artefatos joblib exigem origem confiável, não há autenticação corporativa, o feedback não tem governança de produção e os cenários sintéticos não cobrem adversários reais.

### Como proteger endpoints administrativos?

Eles ficam desabilitados por padrão. Quando habilitados, exigem token de ambiente comparado em tempo constante. Em produção, eu adicionaria autenticação forte, RBAC, auditoria e segregação de rede.

### Qual é o papel do CodeQL?

Analisar padrões de código associados a vulnerabilidades nas linguagens suportadas. Ele complementa testes e revisão; não prova ausência de falhas.

## DevOps

### O que Docker valida?

Que os Dockerfiles constroem imagens reproduzíveis, que a configuração Compose é válida e que backend e frontend iniciam e respondem aos smoke tests. Isso não é benchmark.

### O que CI executa?

Lint, tipagem, migração, testes e coverage do backend; lint, tipagem, testes e build do frontend; audits de dependências; CodeQL; configuração, builds e smoke test Docker.

### Por que Docker CI?

Docker não estava disponível no ambiente local original. O workflow oferece um runner Linux consistente para validar imagens e integração Compose a cada mudança relevante.

### O que Dependabot faz?

Monitora dependências Python, npm e GitHub Actions e abre propostas de atualização. Cada atualização ainda precisa passar pelos checks e por revisão humana.

## Produto

### Quem usaria FraudLens?

No conceito de produto, um analista de risco ou operações que precisa ordenar eventos e reunir contexto. O projeto atual é educacional e não deve receber dados reais.

### O que o analista faz com um alerta?

Lê a decomposição do score, examina regras e evidências, consulta histórico e relacionamentos e registra uma classificação com comentário. O sistema apoia, mas não substitui a decisão.

### Por que explicabilidade importa?

Porque uma prioridade só é acionável quando a pessoa entende os fatores observados, consegue contestá-los e mantém uma trilha de raciocínio. Também facilita depuração e governança.

### Como priorizar alertas?

Combinando risco, severidade, evidência, capacidade operacional e objetivos de recall/precision. Em produção, filas também deveriam considerar impacto, segmento e SLA.

### Como medir valor de negócio?

Tempo de investigação, taxa de confirmação por faixa, perda evitada, custo por alerta revisado, cobertura dos casos relevantes, impacto em clientes e estabilidade ao longo do tempo — sempre comparados a um baseline.

## Limitações

### O FraudLens está production-ready?

Não. É uma demonstração educacional bem testada, mas dados reais exigiriam validação temporal, governança, autenticação, observabilidade, escala, privacidade, fairness, resposta a incidentes e responsabilidade operacional.

### As métricas podem ser comparadas às de um banco?

Não. O gerador e os cenários são controlados e mais simples que o mundo real. As métricas servem para validar a implementação e discutir trade-offs dentro do experimento sintético.

### Por que não há streaming?

Batch favorece reprodução determinística e mantém o escopo alinhado ao MVP. Streaming exigiria idempotência, ordenação de eventos, estado de features, filas, reprocessamento e observabilidade adicionais.

### Qual é a principal limitação do modelo?

Ele aprende isolamento, não intenção nem causalidade. Pode sinalizar novidades legítimas, depende da representação por features e usa contamination e limiares heurísticos.

### O que você faria primeiro em uma evolução real?

Definiria o processo de decisão e o custo dos erros, criaria uma base temporal revisada e governada, executaria shadow mode e só então calibraria thresholds e arquitetura com evidência operacional.
