---
name: abrir-pr
description: >-
  Monta a mensagem de abertura de PR (Pull Request) ja preenchida pelo contexto
  do que o dev fez, pronta pra colar no GitHub/GitLab/Bitbucket. Use SEMPRE que
  o dev for abrir/preparar uma PR, por exemplo: "monta a PR", "prepara a PR",
  "abre a PR", "PR pronta", "gera o texto da PR", "descricao da PR", "prepara
  o merge request". A skill le o contexto (branch atual, git diff da base ate
  HEAD, commits), escolhe a base certa, e preenche: TITULO em ingles
  (Conventional Commits) + CORPO em portugues humano, sem travessao nem emoji.
  Entrega o texto pronto (e, se pedido, o comando gh/glab pr create). NUNCA faz
  push, abre a PR ou apaga a branch por conta propria.
---

# Abrir PR (texto pronto, preenchido pelo contexto)

Gera o título + corpo da PR já preenchidos a partir do que o dev fez, no padrão
do projeto. Se o projeto tiver um template de PR (`.github/PULL_REQUEST_TEMPLATE.md`
ou equivalente), lê e preenche; senão, usa o modelo padrão desta skill.

> Antes de mexer em git, vale o `trabalho-seguro`. Esta skill **entrega texto**: não
> pusha, não abre PR e não apaga branch sem pedido explícito.

## Padrão (não negociável)

- **Título:** inglês, Conventional Commits (`<tipo>(<escopo>): <resumo>`). Casa com os commits.
- **Corpo:** português humano, tom simples. Segue a skill `comentarios-task-commits`.
- **Sem travessão e sem emoji** em nada.
- **Base da PR:** descubra a base correta pelo fluxo do projeto. Branches comuns:
  `develop`, `main`, `staging`, `release`, `testdrive`. Se não der pra inferir,
  **pergunte** qual a base.
- **Branch nunca é apagada** sem pedido explícito. Nada de segredo no diff (`.env`,
  chaves, tokens, credenciais ficam locais).
- **Ninguém aprova o próprio código.** Lembre o dev de pedir review a outro membro.

## Procedimento

1. **Reancorar** (não altera nada):
   ```bash
   git branch --show-current            # nome da branch (traz o tipo e escopo)
   git status -sb
   ```
   Confirme a **base** da PR. Tente inferir pelo nome da branch e pelo fluxo do
   projeto. Se não der pra inferir, pergunte.

2. **Levantar o contexto** contra a base escolhida (`BASE`):
   ```bash
   git log BASE..HEAD --oneline         # o que essa branch adicionou
   git diff BASE...HEAD --stat          # arquivos/áreas tocadas
   git diff BASE...HEAD                 # detalhe (leia o suficiente pra resumir)
   ```
   Extraia do nome da branch: **tipo** (`feat`/`fix`/`refactor`/...) e a
   **descrição**. Nomes comuns: `feat/descricao`, `fix/descricao`,
   `feat/<id-task>(descricao)`, `feature/descricao`.

   Se o nome da branch contém um ID de task (Jira, Monday, ClickUp, etc.),
   preserve-o para referência na PR.

3. **Verificar se existe template de PR** no projeto:
   ```bash
   # GitHub
   cat .github/PULL_REQUEST_TEMPLATE.md 2>/dev/null || \
   cat .github/pull_request_template.md 2>/dev/null || \
   # GitLab
   cat .gitlab/merge_request_templates/*.md 2>/dev/null || \
   echo "Sem template, usar modelo padrao"
   ```
   Se existir, leia e preencha cada seção. Se não, use o modelo padrão abaixo.

4. **Preencher** o título + corpo:
   - **Título** (EN): `tipo` da branch/commits + `escopo` (módulo mais tocado) +
     resumo curto do diff.
   - **Task / Base:** ID da task (se houver) + a base escolhida.
   - **Contexto** (PT): o porquê, curto.
   - **O que mudou** (PT): bullets a partir dos commits + diff, agrupados por área.
   - **Como testar** (PT): passos pro QA/revisor reproduzir.
   - **Evidências:** deixe em branco (o dev anexa prints/video).
   - **Checklist:** o fixo do template ou o padrão abaixo.

5. **Entregar** o título + corpo prontos pra colar. Se o dev pedir, ofereça o
   comando:
   ```bash
   # GitHub
   gh pr create -B <BASE> -H <branch> -t "<titulo>" -F <arquivo-corpo.md>
   # GitLab
   glab mr create -b <BASE> -s <branch> -t "<titulo>" -F <arquivo-corpo.md>
   ```
   **Não rode** esse comando sem permissão explícita.

6. **Conferir antes de entregar:**
   - Título em EN e no formato Conventional Commits
   - Corpo em PT humano
   - Sem travessão/emoji
   - Base coerente com o fluxo
   - Nenhum segredo citado no resumo
   - Lembretes: fez o pré-teste como usuário? Testes do código novo escritos?
     Cole o link da PR na task depois de abrir. Peça review a outro dev.

## Modelo padrão de corpo (quando não há template)

```markdown
## Task
[<ID-DA-TASK>](<link-para-task>) · Base: `<base>`

## Contexto
<Por que essa mudança é necessária, em 1-2 frases.>

## O que mudou
- <bullet 1: o que mudou e onde>
- <bullet 2>
- <bullet 3>

## Como testar
1. <passo 1>
2. <passo 2>
3. Verificar que <resultado esperado>

## Evidências
<prints, videos ou logs do dev — deixar em branco para o dev preencher>

## Checklist
- [ ] Código compila sem erros (`flutter build` / `dart analyze`)
- [ ] Testes do código novo escritos e passando
- [ ] Testei manualmente como usuário
- [ ] Sem segredos/credenciais no diff
- [ ] PR revisada por outro dev (sem self-approve)
```

## Gotchas

- Se o projeto tem **múltiplos ambientes de PR** (ex.: revisão → `testdrive`,
  pós-teste → `release`), adapte a base ao momento. Na dúvida, pergunte.
- No **retrabalho** (correções pós-review), pode ser uma **nova PR na mesma branch**
  (sem apagar): o corpo pode focar no que a correção mudou desde a última revisão.
- Não invente evidências nem passos de teste que você não consegue derivar do diff;
  deixe placeholders claros pro dev completar.
- Se o projeto usa **squash merge**, o título da PR vira a mensagem do commit no
  histórico — capriche mais ainda no título.
- Em projetos com **CI/CD**, mencione se os checks passaram ou se há pipeline pendente.

## Referências

- `.github/PULL_REQUEST_TEMPLATE.md` (ou equivalente): o corpo que a plataforma
  pré-preenche na descrição da PR.
- Skill `comentarios-task-commits`: o estilo (EN técnico no título, PT humano no
  corpo, sem travessão/emoji).
- Skill `trabalho-seguro`: gates de segurança antes de qualquer ação git.
