# FraudLens Portfolio Pack

Este diretório transforma o FraudLens em uma narrativa curta, visual e verificável para LinkedIn, entrevistas, processos seletivos e conversas com pessoas de produto, engenharia, dados e segurança.

O ponto central é simples: o FraudLens não é apenas um modelo de machine learning. É um sistema full stack que transforma pagamentos sintéticos em sinais de risco explicáveis e investigáveis, sempre com decisão humana no final do fluxo.

## Conteúdo

| Material                                           | Uso                                                |
| -------------------------------------------------- | -------------------------------------------------- |
| [CAROUSEL.md](CAROUSEL.md)                         | Roteiro e narrativa dos sete slides                |
| [LINKEDIN_POST.md](LINKEDIN_POST.md)               | Post recomendado, versão curta e versão técnica    |
| [RECRUITER_PITCH.md](RECRUITER_PITCH.md)           | Pitches de 15, 30, 60 e 90 segundos                |
| [TECHNICAL_PITCH.md](TECHNICAL_PITCH.md)           | Explicações técnicas de 30 segundos, 2 e 5 minutos |
| [INTERVIEW_CHEATSHEET.md](INTERVIEW_CHEATSHEET.md) | Perguntas e respostas para entrevistas             |
| [assets/](assets/)                                 | Slides finais em PNG, 1080 × 1350 px               |
| [source/](source/)                                 | HTML, CSS e script Playwright reproduzíveis        |

## Carrossel

O carrossel apresenta uma sequência de sete ideias:

1. a proposta do FraudLens;
2. o problema de transformar volume em atenção;
3. o pipeline de detecção e explicação;
4. a experiência de investigação;
5. a arquitetura full stack;
6. os resultados sintéticos medidos;
7. o aprendizado e o convite para explorar o repositório.

Cada slide funciona isoladamente, mas a sequência foi desenhada para sair de uma pergunta de produto, passar pela implementação e terminar em aprendizado.

## Como regenerar as imagens

Pré-requisitos: Node.js 24, dependências do frontend instaladas e Chromium do Playwright disponível.

Na raiz do repositório:

```bash
npm --prefix frontend ci
npm --prefix frontend exec -- playwright install chromium
node docs/portfolio/source/capture-carousel.mjs
```

O script abre [carousel.html](source/carousel.html), captura cada elemento `.slide` e grava sete PNGs em `docs/portfolio/assets/`. A execução falha se a quantidade de slides ou as dimensões esperadas não forem respeitadas.

## Fontes visuais

As composições reutilizam screenshots reais de `docs/images/` sem modificar seus números ou conteúdo factual. Molduras, recortes e sombras servem apenas para organizar a narrativa.

## Social preview do GitHub

Recomendação: usar `docs/images/linkedin-cover.png` como Social Preview do repositório. Sua proporção horizontal de 1200 × 627 px é mais adequada ao cartão do GitHub do que o slide vertical de capa, embora ambos sigam a mesma identidade visual.

O GitHub CLI e a API pública não oferecem uma operação estável para configurar essa imagem. Faça o ajuste manualmente em:

```text
Settings → General → Social preview
```

Não há website configurado para o repositório.

## Uso responsável

Todos os dados, rótulos e cenários são sintéticos. Recall, precision e PR-AUC descrevem apenas a execução documentada do experimento e não representam desempenho esperado em produção. O risk score é prioridade de investigação, nunca probabilidade ou prova de fraude.
