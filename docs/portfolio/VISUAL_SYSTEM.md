# FraudLens Visual System

## Concept

**Financial Forensics** transforma a investigação de pagamentos na própria identidade visual. O sistema combina capa editorial de tecnologia, arquivo técnico, terminal financeiro e dossiê de evidências sem recorrer a símbolos policiais, clichês de hacker ou decoração sem significado.

Três explorações foram produzidas para a capa:

- **Concept A — Editorial typography:** nome monumental, prioridade investigativa e microdados conectados.
- **Concept B — Evidence board:** screenshot real, ficha em papel e marcações manuais de evidência.
- **Concept C — Financial terminal:** registros densos, estado monitorado e seleção de uma operação.

O Concept A foi escolhido como direção principal por ter a silhueta mais reconhecível, maior impacto em feed e melhor equilíbrio entre tensão e clareza. O sistema final incorpora a materialidade documental do B no slide de evidências e a densidade funcional do C nos slides de volume e sinais.

## Visual philosophy

Cada página deve sugerir duas ideias em sequência: “há algo acontecendo nestes dados” e “é possível explicar por quê”. Uma composição pode ser intensa, mas nunca acusatória. O projeto investiga sinais, não declara fraude.

Cada slide possui uma única ideia visual dominante. Estruturas de apresentação corporativa — títulos seguidos por cards, mockups de dispositivo e grids simétricos — não fazem parte do sistema.

## Color palette

| Papel               | Cor       | Uso                                                        |
| ------------------- | --------- | ---------------------------------------------------------- |
| Investigation black | `#07090B` | Canvas principal                                           |
| Structural black    | `#0B0F12` | Camadas e áreas técnicas                                   |
| Deep graphite       | `#101519` | Fragmentos de interface                                    |
| Evidence paper      | `#E7E5DF` | Headline, informação primária e documentos                 |
| Muted metal         | `#858B8F` | Metadados, rótulos auxiliares e linhas secundárias         |
| Signal red          | `#FF3B30` | Anomalia, evidência, seleção, conexão e ponto de atenção   |
| Validation green    | `#B7FF3C` | Reservado a estados confirmados; não usado decorativamente |

O vermelho ocupa uma fração pequena da página. Ele sempre carrega significado e nunca funciona como brilho ambiental.

## Typography

- **Display:** `Impact`, com fallback para `Arial Narrow` e sans-serif do sistema. Uso em poucas palavras, números gigantes e frases-manifesto.
- **Text:** Arial/Helvetica para explicações curtas em português.
- **Data:** Consolas, com fallback para Courier New e monospace. Uso em IDs, timestamps, métricas, nomes de regras, especificações e labels.
- Fontes não são versionadas nem carregadas de serviços externos.

## Grid

- Canvas mestre: `1080 × 1350 px`.
- Margem editorial de referência: `58 px`.
- Grid técnico subjacente: módulos de `36 px`, com contraste mínimo.
- Composições podem romper o grid, sobrepor regiões e usar cortes intencionais.
- O índice vertical fica na borda direita; o identificador do arquivo permanece no alto à esquerda.

## Spacing

- `8–14 px`: microdados, labels e separação interna.
- `22–36 px`: blocos de informação relacionados.
- `54–72 px`: margens e divisões editoriais.
- Grandes áreas vazias são parte da hierarquia, não espaço a preencher.

## Signal system

- Linha vermelha contínua: trilha da investigação entre slides.
- Quadrado vermelho: evento localizado.
- Círculo e crosshair: prioridade selecionada para análise.
- Contorno vermelho: elemento em revisão, nunca confirmação de fraude.
- Linha cinza fina: relação contextual ou estrutura.

## Evidence markers

O padrão é `EVIDENCE / 01`, seguido por uma descrição factual curta. Screenshots sempre recebem um marcador, origem visual reconhecível e indicação de dados sintéticos.

## Number treatment

Números essenciais usam escala editorial e tipografia condensada. Métricas não compartilham cards idênticos: a hierarquia reflete a narrativa. Precision e disclaimers nunca podem ser ocultados por escala, contraste ou posição.

## Screenshot treatment

- Usar somente capturas reais de `docs/images/`.
- Recortar, ampliar, inclinar levemente e anotar sem editar o conteúdo factual.
- Evitar browser chrome, laptops, celulares ou molduras de produto.
- Preservar elementos suficientes para reconhecer a interface.
- O screenshot `alert-detail.png` não é usado porque a captura existente não contém conteúdo de detalhe utilizável.

## Texture

Ruído fino e grid técnico são aplicados com CSS/SVG em baixa opacidade. Eles reduzem a aparência de superfície digital perfeita sem simular VHS, glitch ou cyberpunk.

## Do

- Usar tensão entre headline condensada e microtipografia monoespaçada.
- Fazer cada linha, marcador e cor cumprir uma função.
- Manter prioridade humana e natureza sintética explícitas.
- Testar cada slide em `1080 × 1350` e `360 × 450`.
- Avaliar os sete slides juntos no contact sheet.

## Don't

- Não usar gradientes azul/roxo, glassmorphism, glow ou blobs.
- Não estruturar páginas como coleções de cards.
- Não usar ícones genéricos, ilustrações de IA ou símbolos de hacker.
- Não inventar transações, sinais, scores ou métricas.
- Não transformar score em probabilidade ou veredito.
