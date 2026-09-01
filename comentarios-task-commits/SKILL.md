---
name: comentarios-task-commits
description: >-
  Escreve comentarios para ferramentas de gestao (Jira, Monday, ClickUp, Trello,
  Linear, etc.) e mensagens de commit no jeito de falar do usuario. Use SEMPRE
  que ele pedir um comentario/atualizacao para a task (board, card, tarefa,
  "escreve pro jira/monday/clickup", "comentario da tarefa", "atualiza o card")
  OU uma mensagem de commit, OU disser "pode commitar" / "faz o commit" /
  "commita isso". Comentario de task = portugues, humano, simples, primeira
  pessoa do singular, titulo em negrito + descricao em blockquote, leve e sem
  termos tecnicos. Commit = ingles, Conventional Commits, corpo tecnico
  detalhado com secao Evidence. Em AMBOS: nunca use travessao nem emoji. Nunca
  misture os dois estilos; se pedir os dois de uma vez, entregue primeiro o
  comentario da task e depois a mensagem de commit.
---

# Comentários de task e mensagens de commit (estilo do usuário)

Ajude a escrever comentários para ferramentas de gestão de projetos (Jira, Monday,
ClickUp, Trello, Linear, Asana, etc.) e mensagens de commit seguindo o jeito de
falar do usuário. São dois registros bem diferentes: o comentário de task é humano
e simples em português; o commit é técnico e detalhado em inglês. **Nunca misture.**

## Regras gerais (valem para os dois)

- **Nunca use travessão** (— ou –). Use vírgula, ponto, ou reescreva a frase.
- **Nunca use emoji.**
- Não deixe o texto formal demais. Escreva de forma humana, simples e natural.
- Quando escrever como se fosse o usuário, use **primeira pessoa do singular**:
  "Eu fiz", "Ajustei", "Validei", "Corrigi", "Conferi".

---

## Comentários para a task (Jira, Monday, ClickUp, etc.)

Português, leve, claro, sem muita coisa técnica. Deve parecer que o próprio
usuário escreveu, explicando o que foi feito, validado ou ajustado, sem entrar em
detalhes de código.

### Formato obrigatório

O título vem **em negrito, numa linha própria** (markdown `**Título**`). A
descrição vem logo abaixo, dentro de um **box de citação** (blockquote, com `>`).
O título **não** entra no box, fica em negrito acima dele.

```markdown
**Título do comentário**

> Descrição do comentário, em primeira pessoa, explicando o que eu fiz, o que
> validei e se ficou tudo certo.
```

### Vocabulário por tipo de comentário

- **Teste/validação:** "Validei", "Testei", "Conferi", "Sem problemas
  encontrados", "Funcionando corretamente".
- **Correção:** "Ajustei", "Corrigi", "Atualizei", "Agora o comportamento está
  correto".
- **Implementação:** "Implementei", "Criei", "Adicionei", "Integrei".
- **Review/análise:** "Revisei", "Analisei", "Verifiquei", "Identifiquei".
- **Progresso/update:** "Avancei", "Finalizei", "Atualizei", "Em andamento".

### Evite jargão; prefira linguagem natural

- Evite: "Foi alterada a lógica de estado assíncrono do componente."
- Prefira: "Ajustei o comportamento para atualizar corretamente depois de salvar."

### Exemplos de estilo

**Exemplo 1 — Validação**

```markdown
**Teste da troca do mix no app**

> Teste da troca do mix realizado no app, sem problemas encontrados. Ao mudar o
> mix, a listagem do cronograma muda corretamente, o conteúdo é redistribuído
> pelas semanas e o valor do mix é salvo. Além disso, validei o refresh da lista
> logo após salvar, recarregando o cronograma e as recomendações.
```

**Exemplo 2 — Implementação**

```markdown
**Implementação do filtro por categoria**

> Implementei o filtro por categoria na listagem principal. Agora o usuário
> consegue selecionar uma ou mais categorias e a lista atualiza em tempo real.
> Testei com diferentes combinações e o comportamento ficou correto.
```

**Exemplo 3 — Correção**

```markdown
**Correção do loading infinito na tela de detalhes**

> Corrigi o problema do loading que ficava infinito quando o usuário acessava a
> tela de detalhes sem conexão. Agora aparece a mensagem de erro corretamente e
> o botão de tentar novamente funciona.
```

---

## Mensagens de commit

Inglês, **Conventional Commits**, título curto e direto. O corpo deve ter o
**máximo de informação técnica possível**: o que mudou, por que mudou, como foi
validado e quais evidências foram coletadas.

Tipos: `fix:` `feat:` `refactor:` `test:` `chore:` `docs:` `style:` `perf:`
`ci:` `build:` (com `(scope)` quando fizer sentido).

Sempre que existirem evidências, inclua no corpo: arquivos alterados;
comportamento antes e depois; testes executados; prints, logs ou resultados
observados; validações manuais feitas; impactos esperados; riscos/pontos de
atenção.

### Formato recomendado

```
type(scope): short description

Detailed description:

Explain the technical changes made.
Explain why the change was necessary.
Mention the affected files, functions or flows when relevant.
Include collected evidence.
Include tests or manual validations performed.

Evidence:

Manual validation:
Logs checked:
Screenshots reviewed:
Tests executed:
Result:
```

### Exemplo

```
fix(schedule): refresh recommendations after mix update

Detailed description:

Updated the mix change flow to refresh the schedule list after saving.
Ensured that recommendations are reloaded with the updated mix value.
Adjusted the save flow to keep the selected group size persisted correctly.
Verified that the weekly schedule is redistributed after changing the mix.

Evidence:

Manual validation completed in the app.
Confirmed that changing the mix updates the schedule list correctly.
Confirmed that the selected mix value remains saved after the update.
Confirmed that recommendations are refreshed after saving.
No issues found during validation.
```

### Quando o usuário disser que pode commitar

Faça o commit de fato (não só escreva a mensagem). Siga as convenções do repo ao
efetivar: se estiver no branch padrão (`main`/`master`/`develop`), **não commite
diretamente**: crie um branch antes ou pergunte. Use staging cirúrgico (`git add`
dos arquivos relevantes, não `git add .` cegamente). Confira o stage com
`git diff --staged` antes de commitar. Nunca `--no-verify`, nunca `--force-push`.

> Se o projeto tiver uma skill separada de `gerar-commit` com procedimento
> operacional (staging, never-commit list, etc.), use-a para o processo e esta
> skill aqui apenas para o **estilo** da mensagem.

---

## Quando pedir os dois de uma vez

Entregue **primeiro o comentário da task** (português, humano) e **depois a
mensagem de commit** (inglês, técnica). Deixe claro qual é qual. Nunca deixe um
contaminar o estilo do outro.

## Adaptação por ferramenta

O formato base (título em negrito + blockquote) funciona bem em todas as
ferramentas que suportam markdown. Ajustes por plataforma, se necessário:

- **Jira:** suporta markdown parcial. Se o blockquote (`>`) não renderizar,
  use `{quote}...{quote}` ou apenas o texto indentado.
- **Monday:** markdown completo funciona nos updates.
- **ClickUp:** markdown completo funciona nos comentários.
- **Trello:** markdown funciona nos comentários dos cards.
- **Linear:** markdown completo funciona.
- **Asana:** suporta rich text mas não markdown puro. Adapte para texto simples
  com a mesma estrutura: título em caixa alta ou negrito, descrição abaixo.

Na dúvida sobre o formato da ferramenta, pergunte ao usuário ou entregue em
markdown padrão (é o mais universal).
