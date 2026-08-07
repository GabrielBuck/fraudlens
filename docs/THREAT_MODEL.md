# Threat model

## Escopo e fronteiras

Ativos: integridade de transações e scores, modelo, token administrativo, feedback e disponibilidade. Fronteiras: navegador→frontend, frontend→API, API→banco e pipeline→artefato.

| Ameaça | Abuso | Mitigação atual | Risco residual |
|---|---|---|---|
| Spoofing | Acessar mutações como outro analista | Escopo demo; admin exige token | Feedback público no ambiente local; produção exige SSO/RBAC |
| Tampering | Alterar score ou evidência | API valida payload; componentes derivados não são mutáveis | Administrador do banco local pode editar dados |
| Repudiation | Negar uma revisão | Timestamp e feedback persistidos | Sem identidade forte ou log append-only |
| Information disclosure | Expor stack, token ou artefato | Erro padronizado, logs mínimos, `.env` ignorado | Modo development expõe detalhe de exceção |
| Denial of service | Paginação ou chamadas excessivas | Limite 100 e rate limit local | Sem gateway ou limite distribuído |
| Elevation | Chamar pipeline administrativo | Desabilitado e token via ambiente | Token estático não substitui RBAC |
| Model poisoning | Inserir dados manipulados no treino | Só gerador local e seed controlada | Admin habilitado pode regenerar o conjunto |
| Evasion | Moldar operação para não acionar regra | Modelo multivariado + regras separadas | Conhecimento do sistema permite adaptação |
| Artifact attack | Trocar joblib por payload malicioso | Caminho configurado e geração local | Sem assinatura criptográfica |

## Entradas externas

Query params de filtros/paginação, JSON de status/feedback e token administrativo. Não há upload. FastAPI/Pydantic validam formato e tamanho; comentários ficam como texto React escapado.

## Privacidade e uso indevido

Não há PII, decisão real ou integração bancária. O principal risco social é apresentar score como culpa; a interface e documentação repetem que se trata de prioridade investigativa em dados sintéticos.

## Próximas mitigações

SSO/RBAC, gateway com quotas, TLS, CSP específica do frontend, audit log imutável, assinatura de artefatos, segregação de funções, verificação de proveniência do dataset e testes de abuso automatizados.
