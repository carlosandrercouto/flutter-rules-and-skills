---
name: criar-commit-cz
description: >-
  Gera o texto de commit (tipo + título curto + descrição longa, cada um
  separado) no formato que eu uso com o Commitizen (cz) no terminal. Use
  SOMENTE quando eu mencionar explicitamente commitizen, cz, ".cz-config.js",
  ou pedir "título e descrição longa" pro commit. NÃO use para pedidos
  genéricos de "escreve a mensagem de commit" / "pode commitar" sem menção a
  commitizen: nesse caso siga a convenção do projeto em questão (ex: skill
  comentarios-task-commits, se existir, em inglês/Conventional
  Commits/Evidence). As duas nunca devem se misturar.
---

# Texto de commit para Commitizen (cz)

Gera o texto de commit no formato que eu efetivamente uso pra commitar via
`cz` (Commitizen, a ferramenta de linha de comando que eu uso no terminal
pra gerar commit): tipo, título e descrição longa **em três saídas
separadas**, prontas pra colar nos prompts do `cz`.

O `cz` já me deixa selecionar o **tipo** direto no terminal com as setas, sem
precisar digitar nada. Por isso o tipo vem numa linha própria (só pra eu
saber qual selecionar) e o **Título** vem em outra linha, sem o tipo
grudado na frente, é o que eu efetivamente colo no prompt de texto do `cz`
sem precisar selecionar só um pedaço no meio da string com o mouse.

## Quando usar

Só quando eu citar commitizen/cz explicitamente, ou pedir especificamente
"título e descrição" pro commit. Fora isso, pedidos genéricos de mensagem
de commit ("escreve o commit", "pode commitar") seguem a convenção própria
do projeto (pode ser bem diferente: inglês, Conventional Commits, seção
Evidence). Não misture os dois formatos na mesma resposta.

## Fonte da verdade: só o que está no stage

Antes de escrever qualquer coisa, rode:

```bash
git status --porcelain
git diff --cached --stat
git diff --cached -- <arquivos relevantes>
```

O primeiro caractere de cada linha do `git status --porcelain` é o status
no **stage** (index); o segundo é o status no working tree. Só descreva
arquivos com status na primeira coluna (`M `, `A `, `D `, etc.). Ignore:

- Arquivos só com mudança no working tree (segunda coluna, ex. ` M`), mesmo
  que apareçam no `git status`.
- Arquivos untracked (`??`).
- Qualquer arquivo staged que seja claramente de outra frente de trabalho
  (não relacionado ao que acabou de ser discutido/implementado na
  conversa) — pergunte se não tiver certeza.

Se o stage mudou várias vezes durante a conversa (eu costumo editar os
arquivos ao vivo enquanto conversamos), sempre releia o stage atual com os
comandos acima antes de escrever o texto, não confie em memória de estados
anteriores da conversa.

## Formato

**Saída em duas linhas, sempre separadas** (nunca junte tipo e título na
mesma linha):

```
Tipo: <tipo>
Titulo: (<escopo>): <descrição>
```

**Tipo:** uma palavra só, o mesmo tipo do Conventional Commits (`feat`,
`fix`, `refactor`, `test`, `chore`, `docs`). É só informativo, pra eu saber
qual selecionar nas setas do `cz`; não entra em nenhum outro lugar do texto.

**Título:** o escopo composto entre parênteses, dois pontos, espaço, e a
descrição no imperativo em português. Continua exatamente igual ao que era
antes de existir a linha `Tipo`, só que sem o tipo grudado na frente.

**Escopo composto (`área > alvo`):** o escopo tem dois níveis separados por
`>`, com espaço dos dois lados. O primeiro nível é a **área** do projeto (a
pasta de topo: `modules`, `core`, `data`, `routes`, `docs`, `test`); o
segundo é o **alvo** dentro dela (o módulo ou feature: `home`,
`auth`, `dashboard`, `profile`). Exemplo completo:
```
Tipo: feat
Titulo: (modules > dashboard): adiciona subtítulo explicativo na página principal
```

Regras do escopo:
- Um alvo só. Se o commit toca vários módulos da mesma área, use só a área
  (`Titulo: (modules): ...`); se toca áreas diferentes, prefira quebrar em
  commits separados, ou use a área dominante.
- Sem alvo específico (mudança na raiz da área), use só a área:
  `Titulo: (core): ...`.
- Fora de `lib/`, a área é a pasta de topo do repositório mesmo (`docs`,
  `test`, `ios`, `android`).

**Descrição longa:** parágrafos técnicos em português, cada um começando
com um verbo no imperativo (`Adiciona`, `Implementa`, `Ajusta`, `Cria`,
`Corrige`, `Remove`). Cite arquivos, classes e métodos reais alterados
(não genérico tipo "ajusta lógica de estado" — prefira "adiciona
lastErrorType (ValueNotifier<AppFailure?>) no DashboardController").
Sem seção "Evidence". Sem bullet points a menos que ajude a leitura; prosa
corrida é o padrão.

**Regras que valem sempre:**
- Nunca use travessão (— ou –). Reescreva com vírgula ou ponto.
- Nunca use emoji.

## Quebra de linha vira `|`

Por padrão, entregue a descrição longa como **um único parágrafo sem
quebras de linha reais**, usando `|` no lugar de toda quebra de linha
(inclusive entre parágrafos) — o campo onde eu colo trata Enter como
confirmação/envio, não como quebra de linha. Isso vale tanto para quebra
entre parágrafos quanto para qualquer quebra dentro de um parágrafo longo.

Se eu disser que vou colar em outro lugar que aceita múltiplas linhas (ex.
editor de commit, textarea), pode entregar com quebras de linha normais em
vez de `|` — pergunte se não estiver claro qual é o destino.

## Exemplo

Tipo:
```
feat
```

Título:
```
(modules > dashboard): implementa feedback de falha de rede/genérica com retry
```

Descrição longa (com `|` no lugar de quebra de linha):
```
Adiciona feedback visível ao usuário para falhas de request no módulo dashboard, que antes falhavam silenciosamente. | Implementa lastErrorType (ValueNotifier<AppFailure?>) no DashboardController, setado no branch de falha dos folds que determinam se algum dado chegou a carregar, e limpo no branch de sucesso correspondente. | Cria o widget compartilhado ErrorFeedbackMessage (lib/core/widgets/error_feedback_message.dart), que renderiza ícone, título, mensagem e botão de retry a partir de um AppFailure.
```
