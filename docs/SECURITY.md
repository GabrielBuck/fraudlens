# Segurança técnica

## Práticas implementadas

- Configuração tipada e segredos somente por ambiente.
- ORM e queries parametrizadas; paginação limitada.
- CORS para a origem configurada, métodos/headers mínimos.
- Headers `nosniff`, `DENY`, referrer e permissions policy.
- Correlation ID, logs JSON e respostas sem stack trace fora de desenvolvimento.
- Rate limit demonstrativo de 240 requisições/minuto por cliente/processo.
- Administração desabilitada por padrão e token comparado em tempo constante.
- Dados exclusivamente sintéticos; nenhum upload ou execução arbitrária.
- Dependabot, audit, pip-audit e CodeQL na automação.

## Segredos

`.env` é ignorado. `.env.example` não contém credenciais. O token administrativo deve ser longo, aleatório e injetado no runtime. Logs não devem registrar tokens ou payloads completos.

## Dependências e artefatos

Use lockfiles, aplique patches de segurança e revise alertas automatizados. Joblib pode executar código durante desserialização: carregue apenas o artefato criado localmente em caminho controlado; produção deve usar assinatura e registry.

## Limitações

Rate limit não é distribuído, não há autenticação de usuário, trilha de auditoria imutável nem TLS dentro do Compose local. Esses controles são obrigatórios antes de qualquer exposição real.
