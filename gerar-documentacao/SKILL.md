---
name: gerar-documentacao
description: >-
  Varredura COMPLETA da documentacao de um projeto Flutter: le o historico do git
  desde a ultima passada (baseline), descobre o que e novo/mudou em cada modulo
  ou feature, atualiza todas as docs afetadas (docs/<modulo>/README.md) e
  ressincroniza o indice (docs/index.html) de uma vez. Uso raro e pesado
  (consolidacao antes de um marco, ou depois de muitos merges na main), nao o dia
  a dia. Use quando pedirem: "gera a documentacao completa", "atualiza toda a
  doc", "sincroniza os docs com o codigo", "consolida a documentacao", "roda a
  documentacao geral", "passa o pente fino nos docs", "atualiza o indice das
  docs". E INCREMENTAL: pula modulo/feature sem commit novo desde a baseline (nao
  repassa o que ja esta feito). Para documentar UM modulo isolado durante a tarefa,
  documente manualmente seguindo a anatomia padrao.
---

# Gerar documentação (varredura completa por histórico)

Consolida a documentação de um projeto Flutter de uma vez: olha o que entrou no
código desde a última passada, atualiza a doc de cada módulo/feature que mudou e
põe o índice em dia. É a skill "gerente" do sistema de docs.

> Vale o `trabalho-seguro`. Isto mexe em MUITOS arquivos de doc de uma vez: rode
> deliberado, num momento de consolidação, e nunca commite sem permissão. Não toca
> código-fonte (`lib/`).

## Conceitos

- **Módulo/Feature**: qualquer unidade funcional do projeto que mereça documentação
  própria. Em projetos Flutter, geralmente corresponde a uma pasta dentro de `lib/`
  (ex.: `lib/app/modules/<modulo>/`, `lib/features/<feature>/`, `lib/src/<area>/`).
  A estrutura exata depende do projeto — descubra-a antes de começar.
- **Pasta de docs**: `docs/` na raiz do projeto. Cada módulo documentado fica em
  `docs/<modulo>/README.md`.
- **Hub/Índice**: `docs/index.html` (ou `docs/README.md`), porta de entrada que
  lista todos os módulos documentados.
- **Baseline**: o último ponto (SHA) até onde a documentação já foi gerada. Tudo
  antes dele está coberto; só o que veio depois precisa ser processado.

## O que ela faz (e o que NÃO faz)

- **Faz:** lê `git log` desde a baseline, agrupa o que mudou por módulo, atualiza
  cada `docs/<modulo>/README.md` afetado, mantém o índice com um card por módulo
  documentado, e grava a nova baseline.
- **Não faz:** não reprocessa módulo sem commit novo desde a baseline (incremental);
  não mexe em `lib/`; não altera código de produção.

## Procedimento

### 0. Descobrir a estrutura do projeto

Antes de tudo, entenda como o projeto organiza seus módulos/features:

```bash
# Descubra a estrutura de pastas de features/módulos
ls lib/                     # visão geral
ls lib/app/modules/ 2>/dev/null || ls lib/features/ 2>/dev/null || ls lib/src/ 2>/dev/null
```

Identifique o padrão (ex.: `lib/app/modules/`, `lib/features/`, `lib/src/`) e use-o
nos comandos abaixo no lugar de `<MODULES_PATH>`. Confirme com o usuário se não for
óbvio.

### 1. Achar a baseline (`references/baseline-git.md` tem os detalhes)

- Lê `docs/.docstate.json` (a baseline = último ponto documentado, por módulo).
- **Primeira execução / sem docstate:** escolha uma âncora explícita (um release
  tag, `origin/main` de antes, ou um SHA que o dev indicar) e registre. Diga
  qual âncora usou.
- O dev pode passar um ref alvo ("desde a tag X", "desde o merge Y"): use como
  baseline em vez do docstate.

### 2. Levantar o jump desde a baseline até HEAD

```bash
# Substitua <MODULES_PATH> pelo caminho real do projeto (ex: lib/app/modules/)
git diff --name-only <BASE>..HEAD -- '<MODULES_PATH>' | \
  sed "s#<MODULES_PATH>##" | cut -d/ -f1 | sort -u
```

Isso dá a lista de módulos com novidade. Módulo fora dessa lista **não é tocado**
(já está documentado e não mudou). Para cada módulo da lista, leia os commits e o
diff dele:

```bash
git log --oneline <BASE>..HEAD -- <MODULES_PATH><modulo>/
git diff <BASE>..HEAD -- <MODULES_PATH><modulo>/
```

### 3. Atualizar a doc de cada módulo afetado

Em `docs/<modulo>/README.md`, seguindo a anatomia padrão (ver seção abaixo):
atualiza as seções que mudaram, preserva o resto, cria o `README.md` se o módulo
ainda não tem doc. Mesmo estilo, mesmas regras (link relativo, sem segredo, sem
inventar).

### 4. Ressincronizar o índice (`references/indice-hub.md`)

No `docs/index.html` (ou `docs/README.md`), garanta uma entrada por módulo
documentado. Adicione o que falta, atualize a descrição do que mudou, remova
entrada de doc que não existe mais.

### 5. Gravar a nova baseline

Escreva HEAD (e o SHA por módulo processado) de volta no `docs/.docstate.json`,
pra próxima passada saber de onde continuar.

### 6. Validar e reportar

Links relativos resolvem; o hub abre sem link quebrado; liste módulos atualizados,
módulos pulados (sem novidade) e o novo baseline SHA.

## Anatomia padrão do README.md de módulo

Cada `docs/<modulo>/README.md` deve seguir esta estrutura:

```markdown
# <Nome do Módulo>

## Visão geral
Uma frase descrevendo o que o módulo faz e seu papel no app.

## Estrutura
Mapa das pastas e arquivos principais, com breve descrição de cada um.

## Arquitetura
- Gerenciamento de estado usado (BLoC, Riverpod, Provider, etc.)
- Padrões aplicados (repository, use case, etc.)
- Dependências principais (pacotes externos relevantes)

## Fluxos principais
Descrição dos fluxos de usuário ou de dados mais importantes.

## Dependências internas
Quais outros módulos/packages do projeto este módulo consome.

## Telas / Widgets principais
Lista das telas e widgets-chave, com breve descrição.

## Limitações / Dívidas técnicas
O que está pendente, incompleto, ou com workaround.

## Histórico de mudanças relevantes
Commits ou merges notáveis desde a última documentação.
```

Adapte ao que existe — se o projeto já tem um formato de doc, siga-o em vez de
impor este. O objetivo é consistência dentro do projeto, não obediência a um
template externo.

## Regras duras

- **Incremental de verdade.** Módulo sem commit em `<BASE>..HEAD` não entra. O
  objetivo é nunca reescrever doc que já está certa e não mudou.
- **Uma doc por módulo, cada uma no seu arquivo.** Nunca uma doc "geral solta" fora
  de `docs/<modulo>/`. Decisão que atravessa módulos vira ADR em `docs/adr/`, não
  um README compartilhado.
- **Só docs.** Zero `lib/`. Segredo nenhum no texto (tokens, senhas, endpoints
  internos, chaves).
- **O hub é responsabilidade daqui**: esta skill é quem enxerga todos os módulos,
  então é quem mantém o índice coerente.
- **Sem commit sem permissão** (trabalho-seguro). Como mexe em muitos arquivos, ao
  commitar, agrupe por módulo ou num commit de doc claro, e confira que nada de
  `lib/` nem segredo entrou.

## Gotchas

- **"Jump entre mains":** na `main`/`master`, a baseline natural é o último ponto
  documentado; o jump são os merges que entraram desde então. Um release tag é uma
  ótima âncora de baseline.
- **docstate ausente é normal na estreia:** só escolha a âncora com critério e
  registre. Sem baseline, `<BASE>..HEAD` viraria o repo inteiro (custoso e ruidoso).
- **Módulo renomeado/removido:** se a pasta em `lib/` sumiu, marque a doc como
  obsoleta (não apague sem confirmar) e tire a entrada do hub.
- **Projeto sem `docs/`:** crie a estrutura na primeira execução:
  `docs/`, `docs/index.html` (ou `docs/README.md`), `docs/.docstate.json`.

## Referências

- `references/baseline-git.md`: o mecanismo de baseline (docstate.json, o range do
  git, agrupar por módulo, primeira execução, "jump entre mains").
- `references/indice-hub.md`: como manter as entradas de módulo no índice
  (formato + procedimento de sincronização).
